# Placeholder for PDF ingestion and embedding script
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from core.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, PDF_SOURCE_DIR, OLLAMA_EMBEDDING_MODEL
import time
from tqdm import tqdm


def load_and_split_documents():
    """Load PDF documents and split them into chunks."""
    print("="*60)
    print("🚀 PDF Ingestion & Embedding Pipeline")
    print("="*60)
    
    # Get PDF files from configured source directory
    pdf_files = [
        os.path.join(PDF_SOURCE_DIR, f)
        for f in os.listdir(PDF_SOURCE_DIR)
        if f.lower().endswith(".pdf")
    ]

    print(f"Found {len(pdf_files)} PDF files")

    # Load each PDF and extract pages with progress indication
    print("📄 Loading PDFs:", end=" ")
    documents = []
    
    with tqdm(total=len(pdf_files), desc="", leave=False) as pbar:
        for idx, pdf_path in enumerate(pdf_files):
            pdf_name = os.path.basename(pdf_path)
            
            # Initialize PyPDFLoader
            loader = PyPDFLoader(pdf_path)
            
            try:
                # Load pages (returns a list)
                pages = loader.load()
                
                # Extend to maintain a flat list of documents
                documents.extend(pages)
            except Exception as e:
                print(f"\n❌ Error loading {pdf_path}: {str(e)}")
                continue
                
            pbar.set_description(f"📖 Loaded: {pdf_name}")
            pbar.update(1)

    print(f"\n✅ Total documents extracted: {len(documents)}")
    
    if documents:
        print(f"📝 First document preview: {documents[0].page_content[:200]}...")
    
    return documents


def embed_and_store_documents(documents):
    """Create embeddings and store them in ChromaDB."""
    if not documents:
        print("❌ No documents to embed.")
        return

    print("\n🔪 Splitting documents into chunks...")
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )

    # Split documents
    texts = text_splitter.split_documents(documents)
    print(f"✅ Documents split into {len(texts)} chunks.")

    print(f"\n🤖 Initializing embeddings with model: {OLLAMA_EMBEDDING_MODEL}")
    print(f"💾 Creating vector store at: {CHROMA_PERSIST_DIR}")

    # Initialize embeddings
    embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)

    print("\n🔄 Creating embeddings and storing in database...")
    
    # Create the vector store with empty documents first
    vectorstore = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )
    
    # Add documents with progress bar
    print("🧠 Embedding chunks:")
    for i in tqdm(range(len(texts)), desc="Progress"):
        vectorstore.add_documents([texts[i]])
    
    print("\n💿 Vector database created successfully!")

    print(f"\n🎉 Successfully processed {len(texts)} document chunks into the vector database!")


def main():
    """Main function to run the ingestion pipeline."""
    # Create the PDF source directory if it doesn't exist
    os.makedirs(PDF_SOURCE_DIR, exist_ok=True)
    
    # Load and split documents
    documents = load_and_split_documents()
    
    # Embed documents if any were loaded
    embed_and_store_documents(documents)


if __name__ == "__main__":
    main()