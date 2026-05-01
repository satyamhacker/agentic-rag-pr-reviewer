import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from core.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, PDF_SOURCE_DIR, OLLAMA_EMBEDDING_MODEL
from tqdm import tqdm

class PDFEmbedder:
    """
    A class to handle the ingestion of PDF documents, splitting them into chunks,
    and storing their embeddings in a Chroma vector database.
    """
    
    def __init__(self):
        self.pdf_source_dir = PDF_SOURCE_DIR
        self.chroma_persist_dir = CHROMA_PERSIST_DIR
        self.collection_name = CHROMA_COLLECTION_NAME
        self.embedding_model = OLLAMA_EMBEDDING_MODEL
        
    def load_and_split_documents(self):
        """Load PDF documents and split them into chunks."""
        print("="*60)
        print("🚀 PDF Ingestion & Embedding Pipeline")
        print("="*60)
        
        # Create the PDF source directory if it doesn't exist
        os.makedirs(self.pdf_source_dir, exist_ok=True)
        
        # Get PDF files from configured source directory
        pdf_files = [
            os.path.join(self.pdf_source_dir, f)
            for f in os.listdir(self.pdf_source_dir)
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
                    
                    # Update metadata source to use only the basename
                    for page in pages:
                        page.metadata["source"] = pdf_name
                        
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

    def embed_and_store_documents(self, documents):
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

        print(f"\n🤖 Initializing embeddings with model: {self.embedding_model}")
        print(f"💾 Creating vector store at: {self.chroma_persist_dir}")

        # Initialize embeddings
        embeddings = OllamaEmbeddings(model=self.embedding_model)

        print("\n🔄 Creating embeddings and storing in database...")
        
        # Create the vector store with empty documents first
        vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=embeddings,
            persist_directory=self.chroma_persist_dir
        )
        
        # Add documents with progress bar
        print("🧠 Embedding chunks:")
        for i in tqdm(range(len(texts)), desc="Progress"):
            vectorstore.add_documents([texts[i]])
        
        print("\n💿 Vector database created successfully!")
        print(f"\n🎉 Successfully processed {len(texts)} document chunks into the vector database!")

    def run_pipeline(self):
        """Run the full ingestion pipeline."""
        documents = self.load_and_split_documents()
        self.embed_and_store_documents(documents)

if __name__ == "__main__":
    embedder = PDFEmbedder()
    embedder.run_pipeline()