# RAG-Powered API for Scientific Paper Assistance

This project provides a REST API that leverages Retrieval-Augmented Generation (RAG) techniques to assist users in querying scientific papers. It allows users to upload PDF documents, which are then processed and stored in a vector database for efficient retrieval and context-aware question answering. The API is built using FastAPI and integrates with OpenAI's language models.

## Features

- **Upload and Process Documents:** Users can upload PDF documents, which are stored in an S3 bucket and processed into vector embeddings for quick retrieval.
- **Contextual Question Answering:** The API can generate responses to user queries by retrieving relevant context from uploaded documents.
- **Chat History Management:** The API supports chat sessions, where users can ask follow-up questions in the same context. Each session's chat history is stored in a PostgreSQL database.
- **List Uploaded Documents:** Users can retrieve a list of all PDF documents stored in the S3 bucket.
- **Manage Sessions:** Retrieve and delete chat sessions, each identified by a unique session name or ID.

## Getting Started

### Prerequisites

- Python 3.8 or later
- An OpenAI API key
- A PostgreSQL database (e.g., on Heroku)
- AWS S3 bucket for storing PDF files

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/glafk/zeorag.git
    cd zeorag
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables:
    ```bash
    export OPENAI_API_KEY=your-openai-api-key
    export AWS_ACCESS_KEY_ID = your-aws-access-key
    export AWS_SECRET_ACCESS_KEY = your-aws-secret-access-key
    export DATABASE_URL=your-database-url
    export S3_FAISS_BUCKET_NAME=your-s3-bucket-name
    ```

4. Run the FastAPI application:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8001
    ```

## API Reference

### `POST /upload_document/`

Uploads and processes a PDF document.

- **Request:**
  - `file`: The PDF file to be uploaded (multipart/form-data).

- **Response:**
  - `200 OK`: A message indicating that the document was successfully uploaded and processed.
  - `500 Internal Server Error`: If an error occurs during the upload or processing.

### `POST /query`

Queries the RAG model with a user question and session ID.

- **Request:**
  - `question`: The user's question (string).
  - `session_id`: The session identifier (string).

- **Response:**
  - `200 OK`: The response from the RAG model, streamed as plain text.
  - `500 Internal Server Error`: If an error occurs during the query.

### `GET /sessions/{session_id}`

Retrieves the chat history for a given session ID.

- **Path Parameters:**
  - `session_id`: The session identifier (string).

- **Response:**
  - `200 OK`: A list of messages in the session history.
  - `500 Internal Server Error`: If an error occurs during retrieval.

### `DELETE /session/{session_id}`

Deletes the chat history for a given session ID.

- **Path Parameters:**
  - `session_id`: The session identifier (string).

- **Response:**
  - `200 OK`: A message indicating that the chat history was successfully deleted.
  - `500 Internal Server Error`: If an error occurs during deletion.

### `GET /sessions`

Retrieves all sessions that have at least one message.

- **Response:**
  - `200 OK`: A list of sessions, each with a session ID and session name.
  - `500 Internal Server Error`: If an error occurs during retrieval.

### `GET /list_documents`

Lists all PDF documents stored in the S3 bucket.

- **Response:**
  - `200 OK`: A list of PDF document names.
  - `500 Internal Server Error`: If an error occurs during retrieval.

## Architecture

- **FastAPI:** The web framework used for building the API.
- **OpenAI API:** Provides the language model for generating responses.
- **PostgreSQL:** Stores chat history for each session.
- **AWS S3:** Stores the uploaded PDF documents.
- **FAISS Vector Store:** Provides efficient retrieval of document chunks for context-aware answering.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
