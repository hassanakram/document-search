from fastapi import FastAPI, UploadFile, Form
from utils import extract_text_from_pdf, search_query
from elasticsearch import Elasticsearch
from tasks import index_document_task

app = FastAPI()
es = Elasticsearch("http://elasticsearch:9200")
INDEX_NAME = "document_chunks"

@app.post("/ingest")
async def ingest_document(file: UploadFile, doc_name: str = Form(...)):
    """Ingest a document and process indexing in the background."""
    if file.content_type == "application/pdf":
        content = extract_text_from_pdf(file.file)
    else:
        content = (await file.read()).decode("utf-8")
    chunks = content.split("\n\n")  # Split into manageable chunks

    # Enqueue the indexing task
    # index_document_task.delay(INDEX_NAME, doc_name, chunks)
    task_result = index_document_task.apply(args=[INDEX_NAME, doc_name, chunks])

    return {
        "message": "Document indexing completed synchronously",
        "task_result": task_result.result,  # Contains the return value of the task
    }

@app.get("/retrieve")
def retrieve(query: str):
    """Retrieve the most relevant chunks for a query."""
    results = search_query(es, INDEX_NAME, query)
    return {"results": results}