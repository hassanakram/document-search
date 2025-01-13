# Document Search Application with Background Indexing

This project is a **document search application** built using FastAPI, Celery, Redis, and Elasticsearch. It enables users to upload documents, process them into smaller chunks, generate embeddings for each chunk, and index them for efficient retrieval. The application supports both background task processing for document ingestion and real-time retrieval using a query-based search.

## Features

1. **Document Ingestion**
   - Upload plain text or PDF files.
   - Split large documents into smaller chunks (e.g., paragraphs).
   - Generate embeddings for each chunk using a pre-trained model.
   - Index the chunks in Elasticsearch for efficient retrieval.

2. **Background Processing**
   - Uses **Celery** to process document ingestion tasks asynchronously.
   - Tasks are queued in **Redis** and processed by workers, ensuring scalability.

3. **Search and Retrieval**
   - Accepts user queries and retrieves the most relevant chunks using cosine similarity between query embeddings and indexed embeddings.
   - Displays the source document and chunk details.
  
## Technology Stack

| Component           | Technology           | Purpose                                  |
|---------------------|----------------------|------------------------------------------|
| **Backend**         | FastAPI              | API for document ingestion and retrieval |
| **Task Queue**      | Celery               | Background task processing               |
| **Message Broker**  | Redis                | Queue for Celery tasks                   |
| **Search Engine**   | Elasticsearch        | Document storage and retrieval           |
| **Embeddings Model**| SentenceTransformers | Generate embeddings for chunks           |

## Setup and Installation

### 1. Clone the Repository
Clone the repository using the following command:

```
git clone https://github.com/your-repo/document-search.git
cd document-search
```

### 2. Build and Start Services
Ensure Docker and Docker Compose are installed. Then run:
```
docker-compose up –build
```



### 3. Access the Application
- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Elasticsearch Dashboard:** [http://localhost:9200](http://localhost:9200)


## Endpoints

### 1. Document Ingestion

Upload a document for indexing.

**POST** `/ingest`

| Parameter      | Type                  | Description              |
|----------------|-----------------------|--------------------------|
| `file`         | `multipart/form-data` | Plain text or PDF file.  |
| `doc_name`     | `string`              | Name of the document.    |

**Example Request:**

```
curl -X POST “http://localhost:8000/ingest” 
-H “Content-Type: multipart/form-data” 
-F “file=@document_1.txt” 
-F “doc_name=Document1”
```

**Response:**
```json
{
  "message": "Document indexing initiated in the background",
  "task_id": "task-id-123"
}
```

**Example Request:**

```
curl -X GET "http://localhost:8000/retrieve?query=search_term"
```

**Response:**
```json
[
  {
    "document_name": "Document1",
    "chunk_number": 1,
    "text": "Relevant text chunk."
  },
  {
    "document_name": "Document1",
    "chunk_number": 2,
    "text": "Another relevant text chunk."
  }
]
```

## How Document Indexing and Searching Works

### 1. Document Ingestion
A user uploads a document via the `/ingest` endpoint. The document is processed as follows:
   - If the file is a PDF, it is converted to plain text using `pdfplumber`.
   - The text is split into smaller, manageable chunks (e.g., paragraphs).
   - Each chunk is passed through a pre-trained embedding model (e.g., SentenceTransformers) to generate a dense vector representation.
   - Metadata (document name, chunk number, text) and embeddings are indexed in Elasticsearch.

This ingestion process is handled asynchronously by Celery workers to improve scalability.

### 2. Query-Based Search
The user submits a search query via the `/retrieve` endpoint. The query is processed as follows:
   - The query is converted into an embedding using the same embedding model used during ingestion.
   - Elasticsearch performs a vector search using cosine similarity between the query embedding and indexed embeddings.
   - The top 3 most relevant chunks are retrieved, including metadata like document name and chunk number.

The results are returned to the user as a JSON response.

## Project Architecture

The following diagram illustrates the high-level architecture of the application:


```
                      +-----------------+
                      |  User Query     |
                      +-----------------+
                              |
                              v
                      +-----------------+
                      | FastAPI Backend |
                      +-----------------+
                        |            |
                        v            v
     +--------------------+        +---------------------+
     | Document Ingestion |        |   Query Processing  |
     +--------------------+        +---------------------+
               |                            |
+-----------------------------+    +-----------------------------+
|    Celery + Redis Queue     |    | Elasticsearch Dense Vectors |
+-----------------------------+    +-----------------------------+
               |                            |
     +--------------------+        +---------------------+
     | Embedding Model    |        | Cosine Similarity   |
     +--------------------+        +---------------------+
                              |
                              v
                      +-----------------+
                      | Search Results  |
                      +-----------------+
```
