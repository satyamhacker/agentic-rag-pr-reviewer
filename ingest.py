# Placeholder for PDF ingestion and embedding script
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from core.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, PDF_SOURCE_DIR, OLLAMA_MODEL
from tqdm import tqdm  # Progress bar ke liye


def load_and_split_documents():
    """Load PDF documents and split them into chunks."""
    # Get PDF files from configured source directory
    pdf_files = [
        os.path.join(PDF_SOURCE_DIR, f)
        for f in os.listdir(PDF_SOURCE_DIR)
        if f.lower().endswith(".pdf")
    ]

    print(f"Found {len(pdf_files)} PDF files")

    # Master documents array
    documents = []

    # Load each PDF with progress bar
    for pdf_path in tqdm(pdf_files, desc="📄 Loading PDFs", unit="file"):
        # Check if file is empty before attempting to load
        if os.path.getsize(pdf_path) == 0:
            tqdm.write(f"⚠️  Skipping empty file: {pdf_path}")
            continue
            
        tqdm.write(f"📖 Loading: {os.path.basename(pdf_path)}")
        
        # Initialize PyPDFLoader
        loader = PyPDFLoader(pdf_path)
        
        try:
            # Load pages (returns a list)
            pages = loader.load()
            
            # Extend to maintain a flat list of documents
            documents.extend(pages)
        except Exception as e:
            tqdm.write(f"❌ Error loading {pdf_path}: {str(e)}")
            continue

    print(f"\n✅ Total documents extracted: {len(documents)}")
    
    if documents:
        print(f"📝 First document preview: {documents[0].page_content[:200]}...")
    
    return documents


def embed_and_store_documents(documents):
    """Create embeddings and store them in ChromaDB."""
    if not documents:
        print("⚠️  No documents to embed.")
        return

    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )

    # Split documents
    print("\n🔪 Splitting documents into chunks...")
    texts = text_splitter.split_documents(documents)
    print(f"✅ Documents split into {len(texts)} chunks.")

    # Initialize embeddings
    print(f"\n🤖 Initializing embeddings with model: {OLLAMA_MODEL}")
    embeddings = OllamaEmbeddings(model=OLLAMA_MODEL)

    print(f"\n🤖 Initializing embeddings with model: {OLLAMA_MODEL}")
    print(f"💾 Creating vector store at: {CHROMA_PERSIST_DIR}")

    # Initialize embeddings
    embeddings = OllamaEmbeddings(model=OLLAMA_MODEL)

    print("\n🔄 Creating embeddings and storing in database...")
    
    # Create the vector store - Chroma from langchain_chroma persists automatically
    vectorstore = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR
    )

    print("💿 Database operations completed!")
    print(f"✅ Documents embedded and stored in {CHROMA_PERSIST_DIR}")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 PDF Ingestion & Embedding Pipeline")
    print("=" * 60)
    
    documents = load_and_split_documents()
    embed_and_store_documents(documents)
    
    print("\n" + "=" * 60)
    print("✨ Pipeline completed successfully!")
    print("=" * 60)