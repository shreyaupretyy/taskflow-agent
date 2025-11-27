from typing import Dict, Any, List, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from app.core.config import settings
import uuid


class VectorDBService:
    """Service for managing vector embeddings and semantic search."""
    
    def __init__(self):
        self.client = chromadb.Client(Settings(
            persist_directory=settings.CHROMA_PERSIST_DIR,
            anonymized_telemetry=False
        ))
        
        # Use sentence-transformers for embeddings (free and local)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.collections = {}
    
    def get_or_create_collection(self, collection_name: str) -> chromadb.Collection:
        """Get or create a ChromaDB collection."""
        if collection_name not in self.collections:
            self.collections[collection_name] = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        return self.collections[collection_name]
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Add documents to a collection with embeddings."""
        collection = self.get_or_create_collection(collection_name)
        
        # Generate IDs if not provided
        if not ids:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to collection
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas or [{}] * len(documents),
            ids=ids
        )
        
        return {
            "success": True,
            "collection": collection_name,
            "count": len(documents),
            "ids": ids
        }
    
    def search(
        self,
        collection_name: str,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for similar documents using semantic search."""
        collection = self.get_or_create_collection(collection_name)
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        return {
            "success": True,
            "query": query,
            "results": [
                {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                }
                for i in range(len(results["ids"][0]))
            ]
        }
    
    def update_document(
        self,
        collection_name: str,
        document_id: str,
        document: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update a document in the collection."""
        collection = self.get_or_create_collection(collection_name)
        
        # Generate new embedding
        embedding = self.embedding_model.encode([document])[0].tolist()
        
        collection.update(
            ids=[document_id],
            documents=[document],
            embeddings=[embedding],
            metadatas=[metadata] if metadata else None
        )
        
        return {
            "success": True,
            "id": document_id,
            "updated": True
        }
    
    def delete_documents(
        self,
        collection_name: str,
        ids: List[str]
    ) -> Dict[str, Any]:
        """Delete documents from a collection."""
        collection = self.get_or_create_collection(collection_name)
        
        collection.delete(ids=ids)
        
        return {
            "success": True,
            "deleted_count": len(ids)
        }
    
    def get_document(
        self,
        collection_name: str,
        document_id: str
    ) -> Dict[str, Any]:
        """Get a specific document by ID."""
        collection = self.get_or_create_collection(collection_name)
        
        result = collection.get(ids=[document_id])
        
        if result["ids"]:
            return {
                "success": True,
                "id": result["ids"][0],
                "document": result["documents"][0],
                "metadata": result["metadatas"][0]
            }
        
        return {
            "success": False,
            "error": "Document not found"
        }
    
    def list_collections(self) -> List[str]:
        """List all collections."""
        collections = self.client.list_collections()
        return [col.name for col in collections]
    
    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """Delete a collection."""
        self.client.delete_collection(name=collection_name)
        
        if collection_name in self.collections:
            del self.collections[collection_name]
        
        return {
            "success": True,
            "collection": collection_name,
            "deleted": True
        }


# Global instance
vector_db = VectorDBService()
