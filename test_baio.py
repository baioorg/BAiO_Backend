from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from baio.src.agents import baio_agent, aniseed_agent
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
    
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        exit(1)
    
    # Run tests
    #results = test_baio_functionality(api_key)

    result = baio_agent(question = "What genes are expressed between stage 1 and 3 in ciona robusta?",
                        llm = ChatOpenAI(model="gpt-4o", temperature=0.3, api_key=api_key),
                        embedding = OpenAIEmbeddings(api_key=api_key))
    
    # Print summary
    print("\nTest Summary:")
    for test_name, result in results.items():
        print(f"\n{test_name}:")
        print(f"Status: {result['status']}")
        if result['status'] == 'Success':
            print(f"Result: {result['result']}")
        else:
            print(f"Error: {result['error']}")