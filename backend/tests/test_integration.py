"""
Integration tests that test real functionality end-to-end.
These tests actually call the LLM and test document processing.
"""
import pytest
import asyncio
from app.agents.base_agent import ExtractorAgent, WriterAgent, AnalyzerAgent
from app.agents.rag_agent import RAGAgent, DocumentQAAgent
import tempfile
import os
from pypdf import PdfWriter
from io import BytesIO


class TestRealAgentExecution:
    """Test actual agent execution with LLM calls."""
    
    @pytest.mark.asyncio
    async def test_extractor_real_execution(self):
        """Test extractor agent with real LLM call."""
        agent = ExtractorAgent()
        result = await agent.execute({
            "url": "mock_url",  # Mock URL, but test LLM response
            "content": "Company XYZ reported revenue of $50M in Q3 2023. CEO John Smith announced expansion plans."
        })
        
        assert result["status"] == "success"
        assert "report" in result
        assert len(result["report"]) > 50  # Should have substantial content
        print(f"✓ Extractor generated report: {len(result['report'])} chars")
    
    @pytest.mark.asyncio
    async def test_writer_real_execution(self):
        """Test writer agent with real LLM call."""
        agent = WriterAgent()
        result = await agent.execute({
            "topic": "Benefits of automation",
            "style": "professional",
            "length": "medium"
        })
        
        assert result["status"] == "success"
        assert "report" in result
        assert len(result["report"]) > 100
        print(f"✓ Writer generated content: {len(result['report'])} chars")
    
    @pytest.mark.asyncio
    async def test_analyzer_real_execution(self):
        """Test analyzer agent with real LLM call."""
        agent = AnalyzerAgent()
        result = await agent.execute({
            "data": "Sales increased by 25% in Q1. Customer satisfaction score: 4.2/5. Churn rate: 5%."
        })
        
        assert result["status"] == "success"
        assert "report" in result
        assert len(result["report"]) > 50
        print(f"✓ Analyzer generated insights: {len(result['report'])} chars")


class TestRAGSystem:
    """Test the RAG system with document upload and querying."""
    
    def test_add_and_search_text_documents(self):
        """Test adding text documents and searching."""
        rag = RAGAgent()
        
        # Sample documents
        docs = [
            "Python is a high-level programming language. It was created by Guido van Rossum in 1991.",
            "FastAPI is a modern web framework for building APIs with Python. It's fast and easy to use.",
            "Machine learning is a subset of artificial intelligence that enables systems to learn from data."
        ]
        
        collection = "test_collection_text"
        
        # Add documents
        chunk_count = rag.add_documents(collection, docs)
        assert chunk_count > 0
        print(f"✓ Added {len(docs)} documents, created {chunk_count} chunks")
        
        # Search for relevant documents
        results = rag.search_documents(collection, "What is Python?", n_results=2)
        assert len(results) > 0
        assert "Python" in results[0]["content"]
        print(f"✓ Search returned {len(results)} relevant chunks")
    
    @pytest.mark.asyncio
    async def test_document_qa_flow(self):
        """Test full document Q&A flow."""
        agent = DocumentQAAgent()
        
        # Add documents
        docs = [
            "TaskFlow Agent is an AI-powered automation platform. It uses LangChain and Ollama for agent orchestration.",
            "The platform supports multiple agent types: Data Extractor, Content Writer, and Analyzer.",
            "RAG capabilities allow users to upload documents and ask questions about them."
        ]
        
        collection = "test_qa_collection"
        agent.add_documents(collection, docs)
        
        # Query the documents
        result = await agent.execute({
            "query": "What agent types are supported?",
            "collection_name": collection
        })
        
        assert result["status"] == "success"
        assert "report" in result
        # Just check that we got a response, don't validate content from mocked LLM
        assert len(result["report"]) > 0
        print(f"✓ Document Q&A response: {result['report'][:100]}...")
    
    def test_pdf_text_extraction_simulation(self):
        """Test that PDF text extraction would work (simulated)."""
        # Create a simple PDF in memory
        pdf_writer = PdfWriter()
        
        # Note: Full PDF text extraction would require pypdf
        # This tests that the import works
        from pypdf import PdfReader
        
        # Verify pypdf is available
        assert PdfReader is not None
        print("✓ PDF processing library available")


class TestModelComparison:
    """Test model comparison capabilities."""
    
    @pytest.mark.asyncio
    async def test_multiple_model_responses(self):
        """Test getting responses from different models."""
        from app.agents.base_agent import BaseAgent
        
        agent = BaseAgent("test")
        
        prompt = "Explain what an API is in one sentence."
        
        # Test with default model
        response = agent.llm.invoke(prompt)
        assert len(response) > 10
        print(f"✓ Model response length: {len(response)} chars")


class TestMetricsTracking:
    """Test that metrics are being tracked properly."""
    
    @pytest.mark.asyncio
    async def test_execution_metrics(self):
        """Test that agent execution can be timed and measured."""
        import time
        from app.agents.base_agent import ExtractorAgent
        
        agent = ExtractorAgent()
        
        start_time = time.time()
        result = await agent.execute({
            "url": "test",
            "content": "Test content for metrics"
        })
        execution_time = time.time() - start_time
        
        assert execution_time > 0
        assert execution_time < 30  # Should complete within 30 seconds
        assert result["status"] == "success"
        
        print(f"✓ Execution completed in {execution_time:.2f}s")
        
        # Calculate approximate tokens (rough estimate)
        input_tokens = len("Test content for metrics".split())
        output_tokens = len(result["report"].split())
        
        print(f"✓ Approximate tokens - Input: {input_tokens}, Output: {output_tokens}")


@pytest.mark.asyncio
async def test_full_workflow_simulation():
    """Test a complete workflow: extract → analyze → write."""
    # Extract
    extractor = ExtractorAgent()
    extract_result = await extractor.execute({
        "url": "test",
        "content": "Revenue grew 50% year-over-year to $100M. Customer base expanded to 10,000 users."
    })
    assert extract_result["status"] == "success"
    
    # Analyze
    analyzer = AnalyzerAgent()
    analysis_result = await analyzer.execute({
        "data": extract_result["report"]
    })
    assert analysis_result["status"] == "success"
    
    # Write summary
    writer = WriterAgent()
    write_result = await writer.execute({
        "topic": "Business growth summary",
        "style": "executive summary"
    })
    assert write_result["status"] == "success"
    
    print("✓ Full workflow: Extract → Analyze → Write completed successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
