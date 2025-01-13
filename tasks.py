from celery_app import celery
from utils import index_document
from elasticsearch import Elasticsearch

es = Elasticsearch("http://elasticsearch:9200")

@celery.task
def index_document_task(index_name, doc_name, chunks):
    """Background task to index document chunks."""
    print(f"Indexing document: {doc_name}")
    index_document(es, index_name, doc_name, chunks)