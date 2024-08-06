import os
import logging
import time

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import FileChatMessageHistory
from print_color import print
from pyfiglet import figlet_format

# Suppress lower-severity messages
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("langchain")
logger.setLevel(logging.ERROR)

def get_chat_history(session_id: str) -> FileChatMessageHistory:
    """Get a chat history from a session id."""
    return FileChatMessageHistory(f'{session_id}.json')


def main():
    # Load API token
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    # Leave temeprature at 0 for easier empirical evaluation
    llm = ChatOpenAI(model="gpt-4o-2024-05-13", temperature=0, api_key=OPENAI_API_KEY)
    embeddings_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model="text-embedding-3-small")

    # Load vector store from local directory
    # Allowing dangersous deserialization of the FAISS index is required
    # Source is trusted
    vector_store = FAISS.load_local("C:/TUE/Thesis/RAG/FAISS",
                                    embeddings=embeddings_model,
                                    allow_dangerous_deserialization=True)

    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')
    # Print the header
    print(figlet_format("ZeoRAG", font="standard"), color="purple", format="bold")

    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    # Create a history aware retriever
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

    # Create rag chain
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    print("Enter session id to load or create a new one:", end=" ", color='magenta', format='bold')
    session_id = input().strip()

    # Clear console and print header
    os.system('cls' if os.name == 'nt' else 'clear')
    print(figlet_format("ZeoRAG", font="standard"), color="purple", format="bold")

    chat_history = get_chat_history(session_id)
    # Print chat history so far
    for message in chat_history.messages:
        if message.type == 'ai':
            print("ZeoRAG:", end=" ", color="blue", format="bold")
            print(f"{message.content}")
            print('\n')
        elif message.type == 'human':
            print("You:", end=" ", color="green", format="bold")
            print(f"{message.content}")
            print('\n')

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history=get_chat_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )

    # Enter into a loop to continuously take user input
    while True:
        try:
            print("You:", end=" ", color="green", format="bold")
            user_input = input().strip()
            print('\n')

            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n")
                print("Exiting ZeoRAG. Goodbye!", color="red", format="bold")
                print("\n")
                time.sleep(1)
                os.system('cls' if os.name == 'nt' else 'clear')
                
                break

            response = conversational_rag_chain.stream({"input": user_input}, config={
                                                        "configurable": {"session_id": session_id}
                                                       })

            try:
                print(f"ZeoRAG:", end=" ", color="blue", format="bold")

                for chunk in response:
                    chunk_text = chunk.get('answer', '')
                    print(chunk_text, end='', flush=True)
                
                print("\n")  # Print a newline after the streaming is complete
            except Exception as e:
                print(f"Error during streaming: {e}")
                print("Sorry, I couldn't find an answer.")

        except KeyboardInterrupt:
            print("\n")
            print("Exiting ZeoRAG. Goodbye!", color="red", format="bold")
            print('\n')
            time.sleep(1)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            break

main()