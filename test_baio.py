from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from baio.src.agents import baio_agent, aniseed_agent, go_nl_agent
import os

def test_baio_functionality(openai_api_key: str):
    """
    Test different functionalities of the baio system
    """
    llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=openai_api_key)
    embedding = OpenAIEmbeddings(api_key=openai_api_key)
    
    # Ensure required directories exist
    os.makedirs("baio/data/persistant_files/vectorstores/ncbi_jin_db_faiss_index", exist_ok=True)
    os.makedirs("baio/data/persistant_files/vectorstores/BLAST_db_faiss_index", exist_ok=True)
    
    # Test cases for different tools
    test_cases = [
        {
            "name": "BLAST Test",
            "query": "Which organism does this DNA sequence come from: AGGGGCAGCAAACACCGGGACACACCCATTCGTGCACTAATCAGAAACTTTTTTTTCTCAAATAATTC",
            "agent": baio_agent,
            "needs_embedding": True
        },
        {
            "name": "ANISEED Test",
            "query": "What genes are expressed between stage 1 and 3 in ciona robusta?",
            "agent": aniseed_agent,
            "needs_embedding": False
        },
        {
            "name": "E-utilities Test",
            "query": "Find information about the TP53 gene",
            "agent": baio_agent,
            "needs_embedding": True
        }
    ]
    
    results = {}
    for test in test_cases:
        print(f"\nRunning {test['name']}...")
        try:
            if test["needs_embedding"]:
                result = test["agent"](test["query"], llm, embedding)
            else:
                result = test["agent"](test["query"], llm)
            results[test["name"]] = {
                "status": "Success",
                "result": result
            }
        except Exception as e:
            results[test["name"]] = {
                "status": "Failed",
                "error": str(e)
            }
        print(f"{test['name']} Result:", results[test["name"]])
    
    return results

if __name__ == "__main__":
    import os
    
    apikey = ""

    os.environ['OPENAI_API_KEY'] = apikey
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=apikey)

    print("results:\n\n", go_nl_agent("What are the GO terms for BRCA1 and TP53?", llm))
    