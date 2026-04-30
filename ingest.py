# Placeholder for PDF ingestion and embedding script
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from core.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, PDF_SOURCE_DIR, OLLAMA_MODEL


def load_and_split_documents():
    """Load PDF documents and split them into chunks."""
    # Get PDF files from configured source directory
    pdf_files = [
        os.path.join(PDF_SOURCE_DIR, f)
        for f in os.listdir(PDF_SOURCE_DIR)
        if f.lower().endswith(".pdf")
    ]

    print(f"Found PDF files: {pdf_files}")

    # Master documents array
    documents = []

    # Load each PDF and extract pages
    for pdf_path in pdf_files:
        # Check if file is empty before attempting to load
        if os.path.getsize(pdf_path) == 0:
            print(f"Skipping empty file: {pdf_path}")
            continue
            
        print(f"Loading: {pdf_path}")
        
        # Initialize PyPDFLoader
        loader = PyPDFLoader(pdf_path)
        
        try:
            # Load pages (returns a list)
            pages = loader.load()
            
            # Extend to maintain a flat list of documents
            documents.extend(pages)
        except Exception as e:
            print(f"Error loading {pdf_path}: {str(e)}")
            continue

    print(f"\nTotal documents extracted: {len(documents)}")
    
    if documents:
        print(f"First document preview: {documents[0].page_content[:2000]}...")
    
    return documents



def embed_and_store_documents(documents):
    """Create embeddings and store them in ChromaDB."""
    if not documents:
        print("No documents to embed.")
        return

    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )

    # Split documents
    texts = text_splitter.split_documents(documents)
    print(f"Documents split into {len(texts)} chunks.")

    # Initialize embeddings
    embeddings = OllamaEmbeddings(model=OLLAMA_MODEL)

    # Create and persist the vector store
    vectorstore = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )

    # Add texts to the vector store
    vectorstore.add_documents(texts)
    vectorstore.persist()

    print(f"Documents embedded and stored in {CHROMA_PERSIST_DIR}")


documents = load_and_split_documents()
embed_and_store_documents(documents)