import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document

def setup_test_vectorstores(openai_api_key: str):
    """
    Initialize test vector stores with minimal test data
    """
    embedding = OpenAIEmbeddings(api_key=openai_api_key)
    
    # Create base directories
    base_dir = "baio/data/persistant_files/vectorstores"
    os.makedirs(f"{base_dir}/ncbi_jin_db_faiss_index", exist_ok=True)
    os.makedirs(f"{base_dir}/BLAST_db_faiss_index", exist_ok=True)
    
    # Sample documents for NCBI
    ncbi_docs = [
        Document(
            page_content="TP53 is a tumor suppressor gene involved in cell cycle regulation",
            metadata={"source": "ncbi"}
        ),
    ]
    
    # Sample documents for BLAST
    blast_docs = [
        Document(
            page_content="AGGGGCAGCAAACACCGGG is a DNA sequence found in multiple organisms",
            metadata={"source": "blast"}
        ),
    ]
    
    # Create and save vector stores
    ncbi_db = FAISS.from_documents(ncbi_docs, embedding)
    blast_db = FAISS.from_documents(blast_docs, embedding)
    
    ncbi_db.save_local(f"{base_dir}/ncbi_jin_db_faiss_index")
    blast_db.save_local(f"{base_dir}/BLAST_db_faiss_index")
    
    print("Vector stores initialized with test data")

if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        exit(1)
    
    setup_test_vectorstores(api_key)
