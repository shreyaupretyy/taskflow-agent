import pickle
from pathlib import Path
from typing import Any, Dict, List

import faiss
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.agents.base_agent import BaseAgent


class RAGAgent(BaseAgent):
    """Agent that uses Retrieval Augmented Generation for document-based Q&A."""

    def __init__(self):
        super().__init__("RAG")

        # Directory to store FAISS indices
        self.index_dir = Path("data/faiss_indices")
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Dictionary to hold FAISS indices in memory
        self.indices = {}
        self.document_stores = {}

        # Check for GPU availability
        self.use_gpu = self._has_cuda()

        # Initialize embeddings model (free, local)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cuda" if self.use_gpu else "cpu"},
        )

        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        self.system_prompt = (
            """You are a helpful AI assistant that answers questions """
            """based on provided context."""
        )
        self.system_prompt += """

Use ONLY the information from the provided context to answer the question.
If the answer is not in the context, say "I don't have enough information "
"in the provided documents to answer this question."

Format your response as follows:

ANSWER
[Your answer based on the context]

SOURCES
[List the relevant document sections you used]

CONFIDENCE
[High/Medium/Low based on how well the context supports your answer]"""

    def _has_cuda(self) -> bool:
        """Check if CUDA is available for GPU acceleration."""
        try:
            import torch

            return torch.cuda.is_available()
        except ImportError:
            return False

    def _get_or_create_index(self, collection_name: str):
        """Get or create a FAISS index for a collection."""
        if collection_name not in self.indices:
            index_path = self.index_dir / f"{collection_name}.index"
            docs_path = self.index_dir / f"{collection_name}.pkl"

            if index_path.exists() and docs_path.exists():
                # Load existing index
                self.indices[collection_name] = faiss.read_index(str(index_path))
                with open(docs_path, "rb") as f:
                    self.document_stores[collection_name] = pickle.load(f)
            else:
                # Create new index (384 is the dimension for all-MiniLM-L6-v2)
                self.indices[collection_name] = faiss.IndexFlatL2(384)
                self.document_stores[collection_name] = []

        return self.indices[collection_name], self.document_stores[collection_name]

    def _save_index(self, collection_name: str):
        """Save FAISS index and document store to disk."""
        if collection_name in self.indices:
            index_path = self.index_dir / f"{collection_name}.index"
            docs_path = self.index_dir / f"{collection_name}.pkl"

            faiss.write_index(self.indices[collection_name], str(index_path))
            with open(docs_path, "wb") as f:
                pickle.dump(self.document_stores[collection_name], f)

    def add_documents(
        self, collection_name: str, documents: List[str], metadatas: List[Dict] = None
    ) -> int:
        """Add documents to a FAISS index."""
        try:
            index, doc_store = self._get_or_create_index(collection_name)

            # Split documents into chunks
            all_chunks = []
            all_metadatas = []

            for idx, doc in enumerate(documents):
                chunks = self.text_splitter.split_text(doc)
                all_chunks.extend(chunks)

                # Add metadata for each chunk
                doc_metadata = metadatas[idx] if metadatas and idx < len(metadatas) else {}
                for chunk_idx, chunk in enumerate(chunks):
                    all_metadatas.append(
                        {
                            **doc_metadata,
                            "chunk_index": chunk_idx,
                            "doc_index": idx,
                            "content": chunk,
                        }
                    )

            # Generate embeddings
            embeddings = [self.embeddings.embed_query(chunk) for chunk in all_chunks]
            embeddings_array = np.array(embeddings).astype("float32")

            # Add to FAISS index
            index.add(embeddings_array)

            # Store documents with metadata
            doc_store.extend(all_metadatas)

            # Save to disk
            self._save_index(collection_name)

            return len(all_chunks)
        except Exception as e:
            print(f"Error adding documents: {str(e)}")
            raise

    def search_documents(self, collection_name: str, query: str, n_results: int = 5) -> List[Dict]:
        """Search for relevant documents using FAISS."""
        try:
            index, doc_store = self._get_or_create_index(collection_name)

            if index.ntotal == 0:
                return []

            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            query_vector = np.array([query_embedding]).astype("float32")

            # Search
            n_results = min(n_results, index.ntotal)
            distances, indices = index.search(query_vector, n_results)

            # Format results
            documents = []
            for i, idx in enumerate(indices[0]):
                if idx < len(doc_store):
                    doc = doc_store[idx]
                    documents.append(
                        {
                            "content": doc.get("content", ""),
                            "metadata": {k: v for k, v in doc.items() if k != "content"},
                            "distance": float(distances[0][i]),
                        }
                    )

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
                "report": "No relevant documents found. Please upload documents first.",
            }

        # Build context from relevant documents
        context = "\n\n".join(
            [f"Source {i+1}:\n{doc['content']}" for i, doc in enumerate(relevant_docs)]
        )

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
            "sources_used": len(relevant_docs),
        }


class DocumentQAAgent(RAGAgent):
    """Specialized RAG agent for document Q&A."""

    def __init__(self):
        super().__init__()
        self.name = "DocumentQA"
        self.system_prompt = (
            """You are an expert document analyst that answers questions """
            """precisely based on uploaded documents."""
        )
        self.system_prompt += """

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
