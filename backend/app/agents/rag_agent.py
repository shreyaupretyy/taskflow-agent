from typing import Dict, Any, List
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.agents.base_agent import BaseAgent
from app.core.config import settings
import os


class RAGAgent(BaseAgent):
    """Agent that uses Retrieval Augmented Generation for document-based Q&A."""
    
    def __init__(self):
        super().__init__("RAG")
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        # Initialize embeddings model (free, local)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        self.system_prompt = """You are a helpful AI assistant that answers questions based on provided context.

Use ONLY the information from the provided context to answer the question.
If the answer is not in the context, say "I don't have enough information in the provided documents to answer this question."

Format your response as follows:

ANSWER
[Your answer based on the context]

SOURCES
[List the relevant document sections you used]

CONFIDENCE
[High/Medium/Low based on how well the context supports your answer]"""
    
    def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict] = None) -> int:
        """Add documents to a ChromaDB collection."""
        try:
            # Get or create collection
            collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "User document collection"}
            )
            
            # Split documents into chunks
            all_chunks = []
            all_metadatas = []
            
            for idx, doc in enumerate(documents):
                chunks = self.text_splitter.split_text(doc)
                all_chunks.extend(chunks)
                
                # Add metadata for each chunk
                doc_metadata = metadatas[idx] if metadatas and idx < len(metadatas) else {}
                for chunk_idx, chunk in enumerate(chunks):
                    all_metadatas.append({
                        **doc_metadata,
                        "chunk_index": chunk_idx,
                        "doc_index": idx
                    })
            
            # Generate embeddings and add to collection
            embeddings = [self.embeddings.embed_query(chunk) for chunk in all_chunks]
            
            # Add to ChromaDB
            collection.add(
                embeddings=embeddings,
                documents=all_chunks,
                metadatas=all_metadatas,
                ids=[f"doc_{i}" for i in range(len(all_chunks))]
            )
            
            return len(all_chunks)
        except Exception as e:
            print(f"Error adding documents: {str(e)}")
            raise
    
    def search_documents(self, collection_name: str, query: str, n_results: int = 5) -> List[Dict]:
        """Search for relevant documents."""
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
            
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            documents = []
            if results['documents'] and len(results['documents']) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    documents.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else None
                    })
            
            return documents
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            return []
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute RAG query on documents."""
        query = input_data.get("query", "")
        collection_name = input_data.get("collection_name", "default")
        
        # Search for relevant documents
        relevant_docs = self.search_documents(collection_name, query, n_results=5)
        
        if not relevant_docs:
            return {
                "agent": self.name,
                "status": "success",
                "report": "No relevant documents found. Please upload documents first."
            }
        
        # Build context from relevant documents
        context = "\n\n".join([f"Source {i+1}:\n{doc['content']}" for i, doc in enumerate(relevant_docs)])
        
        # Generate answer using LLM
        prompt = f"""{self.system_prompt}

CONTEXT:
{context}

QUESTION: {query}

Provide your answer based only on the context above."""

        response = self.llm.invoke(prompt)
        
        return {
            "agent": self.name,
            "status": "success",
            "report": response,
            "sources_used": len(relevant_docs)
        }


class DocumentQAAgent(RAGAgent):
    """Specialized RAG agent for document Q&A."""
    
    def __init__(self):
        super().__init__()
        self.name = "DocumentQA"
        self.system_prompt = """You are an expert document analyst that answers questions precisely based on uploaded documents.

Analyze the provided context carefully and answer the question accurately.
If the answer requires synthesizing information from multiple sources, do so clearly.
Always cite which source(s) you're using.

Format your response as follows:

DOCUMENT Q&A REPORT

ANSWER
[Clear, comprehensive answer to the question]

KEY INFORMATION
• [Important point 1]
• [Important point 2]
• [Important point 3]

SOURCES REFERENCED
[Which document sections were most relevant]

CONFIDENCE LEVEL
[High/Medium/Low - explain why]

Be thorough but concise."""
