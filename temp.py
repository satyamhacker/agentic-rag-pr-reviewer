import chromadb
from core.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, OLLAMA_MODEL
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# 1. Connect to raw ChromaDB client to inspect metadata
print("--- Inspecting Raw Database ---")
client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

# List collections
print("Collections:", client.list_collections())

# Get the specific collection
try:
    collection = client.get_collection(CHROMA_COLLECTION_NAME)
    print(f"\nCollection '{CHROMA_COLLECTION_NAME}' Count:", collection.count())
    
    peek_data = collection.peek(limit=1)
    if peek_data and peek_data['ids']:
        print(f"Peek (First ID):", peek_data['ids'][0])
        print(f"Peek (First Metadata):", peek_data['metadatas'][0])
except Exception as e:
    print(f"Could not get collection details: {e}")

# 2. Query test using LangChain integration
print("\n--- Testing Query ---")
embeddings = OllamaEmbeddings(model=OLLAMA_MODEL)
vector_store = Chroma(
    collection_name=CHROMA_COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_PERSIST_DIR
)

query = "HTML headings"
print(f"Querying for: '{query}'")
results = vector_store.similarity_search_with_score(query, k=2)

if results:
    for doc, score in results:
        print(f"\nScore: {score:.4f}")
        print(f"Source: {doc.metadata.get('source')}")
        print(f"Preview: {doc.page_content[:100]}...")
else:
    print("No results found.")
