import os
import logging
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.adapters.openai import convert_message_to_dict
import boto3
import psycopg
import uvicorn

from helpers import get_chat_history, delete_chat_history, stream_rag_response, get_vector_store
from helpers import get_db_connection, load_documents_from_pdfs, split_documents, update_vector_store
from helpers import is_valid_uuid
# from CustomMessageHistory import CustomChatMessageHistory

# Suppress lower-severity messages
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("langchain")
logger.setLevel(logging.ERROR)

# Initalize S3 client
s3 = boto3.client('s3')
S3_BUCKET_NAME = os.environ.get("S3_FAISS_BUCKET_NAME")


# Define the table name
table_name = "chat_history"

# Connect to database
DATABASE_URL = os.environ['DATABASE_URL']
if DATABASE_URL.startswith("postgres://"):
    connection_string = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Commenting this out for now. Keeping it if I need to recreate the table.
# Create the table
# connection = psycopg.connect(connection_string, sslmode='require')
# CustomChatMessageHistory.create_custom_table(connection, table_name)

# Initialize FastAPI app
app = FastAPI()

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Define the request model using Pydantic
class QueryRequest(BaseModel):
    question: str
    session_name: str

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

COLLECTION_NAME = 'papers'
connection = os.environ['DATABASE_URL']
# Replace the postgres:// protocol with postgresql:// to deal with SQLAlchemy
# version 1.4 not supporting postgres:// protocol used by Heroku Postgres
if connection.startswith("postgres://"):
    connection = connection.replace("postgres://", "postgresql://", 1)

# Leave temeprature at 0 for easier empirical evaluation
llm = ChatOpenAI(model="gpt-4o-2024-05-13", temperature=0, api_key=OPENAI_API_KEY)
embeddings_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model="text-embedding-3-small")

vector_store = get_vector_store(embeddings_model,
                                COLLECTION_NAME,
                                connection)

contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    llm, vector_store.as_retriever(), contextualize_q_prompt
)

# Add custom system prompt
system_prompt = """
    You are a highly-skilled AI researcher and you have the task to assist in answering questions on scientific papers. Use the following pieces of retrieved context to answer the question. Be as specific as possible and provide details if needed.

    Context: {context} 

    Answer:
"""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)

@app.get("/sessions/{session_id}")
def get_history(session_id: str):
    """
    Retrieve the chat history for a given session ID.

    Args:
        session_id (str): The session's UUID.

    Returns:
        list: A list of messages in the session history.

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        # If session id is not a valid UUID, convert it to one
        if not is_valid_uuid(session_id):
            session_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, session_id))
        chat_history = get_chat_history(session_id=session_id)

        messages_json = [convert_message_to_dict(message) for message in chat_history.get_messages()]
        return messages_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@app.delete("/sessions/{session_id}")
def delete_history(session_id: str):
    """
    Delete the chat history for a given session ID.

    Args:
        session_id (str): The session's UUID.

    Returns:
        dict: A message indicating the result of the deletion.

    Raises:
        HTTPException: If an error occurs during deletion.
    """
    try:
        # If session id is not a valid UUID, convert it to one
        if not is_valid_uuid(session_id):
            session_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, session_id))
        delete_chat_history(session_id)
        return {"message": f"Chat history for session {session_id} has been deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@app.get("/sessions")
def get_sessions_with_messages():
    """
    Retrieve all sessions that have at least one message.

    Returns:
        list: A list of sessions with session_id and session_name.

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        connection = psycopg.connect(connection_string, sslmode='require')
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT DISTINCT session_id, session_name
                FROM {table_name}
                WHERE message IS NOT NULL;
            """)
            sessions = cursor.fetchall()
        return [{"session_id": str(session[0]), "session_name": session[1]} for session in sessions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


# Define the FastAPI endpoint for querying
@app.post("/query")
async def query_rag(request: QueryRequest):
    """
    Query the RAG model with the user's question and session ID.

    Args:
        request (QueryRequest): The user's query request.

    Returns:
        StreamingResponse: The streaming response from the RAG model.

    Raises:
        HTTPException: If an error occurs during the query.
    """
    try:
        # Use StreamingResponse to stream the RAG model's response
        return StreamingResponse(stream_rag_response(request.question, 
                                                     request.session_name,
                                                     history_aware_retriever,
                                                     question_answer_chain), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@app.post("/upload_document/")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF document, process it, and add it to the vector store.

    Args:
        file (UploadFile): The PDF file to be uploaded.

    Returns:
        dict: A message indicating the result of the upload and processing.

    Raises:
        HTTPException: If an error occurs during the upload or processing.
    """
    try:
        # Read the file first to avoid the upload process closing it
        file_content = await file.read()

        print(f"Uploading {file.filename}...")
        s3.upload_fileobj(file.file, S3_BUCKET_NAME, file.filename)
        print(f"Uploaded {file.filename} to {S3_BUCKET_NAME}.")
        
        # Save the file locally for processing
        local_file_path = f"C:/TUE/Thesis/RAG/papers/{file.filename}"
        with open(local_file_path, 'wb') as f:
            print(f"Writing {file.filename} to {local_file_path}...")
            f.write(file_content)
            print(f"Wrote {file.filename} to {local_file_path}.")

        print(f"Loading {local_file_path}...")
        documents = load_documents_from_pdfs([local_file_path])
        chunks = split_documents(documents)

        connection = get_db_connection()

        update_vector_store(chunks, COLLECTION_NAME, connection)

        # Clean up the local file
        os.remove(local_file_path)

        return {"message": "Document uploaded and processed successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@app.get("/list_documents")
def list_documents():
    """
    Retrieve the names of all PDF documents in the S3 store.

    Returns:
        dict: A dictionary containing the list of PDF documents.

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    try:
        # List all objects in the S3 bucket
        response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)
        
        # Check if there are any contents
        if 'Contents' not in response:
            return {"documents": []}
        
        # Filter out the PDF files
        pdf_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.pdf')]
        
        return {"documents": pdf_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)