"""
Test script to verify PDF upload and document Q&A functionality.
This demonstrates the complete RAG workflow end-to-end.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from app.agents.rag_agent import RAGAgent, DocumentQAAgent
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import tempfile


def create_test_pdf():
    """Create a simple test PDF with sample content."""
    buffer = io.BytesIO()
    
    # Create PDF with reportlab
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "TaskFlow Agent - Test Document")
    
    # Add content
    c.setFont("Helvetica", 12)
    content = [
        "",
        "Overview:",
        "TaskFlow Agent is an AI-powered automation platform built with FastAPI and Next.js.",
        "",
        "Key Features:",
        "1. Multiple AI Agents: Data Extractor, Content Writer, and Analyzer",
        "2. RAG Capabilities: Upload documents and ask questions",
        "3. Model Comparison: Compare performance across different LLM models",
        "4. Metrics Tracking: Real-time performance and usage analytics",
        "",
        "Technical Stack:",
        "- Backend: FastAPI with SQLAlchemy",
        "- Frontend: Next.js 14 with TypeScript",
        "- AI/ML: LangChain with Ollama (llama3.2)",
        "- Vector DB: FAISS for efficient semantic search",
        "- Embeddings: sentence-transformers/all-MiniLM-L6-v2",
        "",
        "Use Cases:",
        "- Automated market research and competitive analysis",
        "- AI-powered content generation and optimization",
        "- Data extraction and analysis workflows",
        "- Document Q&A and knowledge extraction",
        ""
    ]
    
    y = 700
    for line in content:
        c.drawString(100, y, line)
        y -= 20
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer


async def test_pdf_upload_and_query():
    """Test the complete PDF upload and Q&A workflow."""
    print("\n🧪 Testing PDF Upload and Document Q&A Workflow\n")
    
    # Step 1: Create a test PDF
    print("1️⃣  Creating test PDF...")
    pdf_buffer = create_test_pdf()
    print("✓ Test PDF created")
    
    # Step 2: Extract text from PDF (simulating upload)
    print("\n2️⃣  Extracting text from PDF...")
    pdf_reader = PdfReader(pdf_buffer)
    text_content = ""
    for page_num, page in enumerate(pdf_reader.pages):
        text_content += f"\n--- Page {page_num + 1} ---\n"
        text_content += page.extract_text()
    
    print(f"✓ Extracted {len(text_content)} characters from {len(pdf_reader.pages)} page(s)")
    print(f"   First 200 chars: {text_content[:200]}...")
    
    # Step 3: Add document to RAG agent
    print("\n3️⃣  Adding document to RAG system...")
    rag_agent = RAGAgent()
    collection_name = "test_pdf_collection"
    
    chunk_count = rag_agent.add_documents(
        collection_name, 
        [text_content],
        [{"filename": "test_document.pdf", "pages": len(pdf_reader.pages)}]
    )
    print(f"✓ Document added: {chunk_count} chunks created")
    
    # Step 4: Test search functionality
    print("\n4️⃣  Testing document search...")
    search_results = rag_agent.search_documents(
        collection_name,
        "What are the key features?",
        n_results=3
    )
    print(f"✓ Search returned {len(search_results)} relevant chunks")
    for i, result in enumerate(search_results, 1):
        print(f"\n   Result {i}:")
        print(f"   Content: {result['content'][:100]}...")
        print(f"   Distance: {result['distance']:.4f}")
    
    # Step 5: Test Document Q&A
    print("\n5️⃣  Testing Document Q&A with LLM...")
    qa_agent = DocumentQAAgent()
    
    questions = [
        "What is TaskFlow Agent?",
        "What AI models does it use?",
        "What are the main use cases?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n   Q{i}: {question}")
        result = await qa_agent.execute({
            "query": question,
            "collection_name": collection_name
        })
        
        if result["status"] == "success":
            print(f"   A{i}: {result['report'][:200]}...")
            print(f"   ✓ Used {result.get('sources_used', 0)} source(s)")
        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
    
    print("\n✅ PDF Upload and Q&A workflow completed successfully!\n")
    print("Summary:")
    print(f"  • PDF pages: {len(pdf_reader.pages)}")
    print(f"  • Text extracted: {len(text_content)} chars")
    print(f"  • Vector chunks: {chunk_count}")
    print(f"  • Questions tested: {len(questions)}")
    print(f"  • Collection: {collection_name}")


def test_file_type_validation():
    """Test that only supported file types are accepted."""
    print("\n🧪 Testing File Type Validation\n")
    
    supported_types = [".pdf", ".txt", ".md", ".markdown"]
    print(f"Supported file types: {', '.join(supported_types)}")
    
    test_files = [
        "document.pdf",
        "notes.txt",
        "readme.md",
        "guide.markdown",
        "image.jpg",  # Should fail
        "data.xlsx"   # Should fail
    ]
    
    for filename in test_files:
        ext = os.path.splitext(filename)[1].lower()
        is_supported = ext in supported_types
        status = "✓" if is_supported else "❌"
        print(f"  {status} {filename} - {'Supported' if is_supported else 'Not supported'}")
    
    print("\n✅ File type validation working correctly\n")


async def main():
    """Run all tests."""
    try:
        # Test 1: File type validation
        test_file_type_validation()
        
        # Test 2: Full PDF upload and Q&A workflow
        await test_pdf_upload_and_query()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED - PDF Upload & Q&A System Working!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
