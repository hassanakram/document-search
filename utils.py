from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
import pdfplumber

# Load pre-trained model
MODEL = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)

def generate_embeddings(text_chunks):
    """Generate embeddings for text chunks."""
    return MODEL.encode(text_chunks, convert_to_tensor=False).tolist()

def index_document(es, index_name, doc_name, text_chunks):
    """Index document chunks in Elasticsearch."""
    # Define the mapping for the index if it doesn't exist
    if not es.indices.exists(index=index_name):
        es.indices.create(
            index=index_name,
            body={
                "mappings": {
                    "properties": {
                        "document_name": {"type": "keyword"},
                        "chunk_number": {"type": "integer"},
                        "text": {"type": "text"},
                        "embedding": {"type": "dense_vector", "dims": 384},  # Update dims based on your model
                    }
                }
            },
        )

    # Index each chunk
    for i, chunk in enumerate(text_chunks):
        doc = {
            "document_name": doc_name,
            "chunk_number": i + 1,
            "text": chunk,
            "embedding": generate_embeddings([chunk])[0],
        }
        es.index(index=index_name, document=doc)


def search_query(es, index_name, query, top_k=3):
    """Search for the most relevant chunks."""
    query_vector = generate_embeddings([query])[0]
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                "params": {"query_vector": query_vector},
            },
        }
    }
    response = es.search(index=index_name, query=script_query, size=top_k)
    return [
        {
            "document_name": hit["_source"]["document_name"],
            "chunk_number": hit["_source"]["chunk_number"],
            "text": hit["_source"]["text"],
        }
        for hit in response["hits"]["hits"]
    ]