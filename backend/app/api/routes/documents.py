from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.security import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.agent_execution import DocumentStore
from app.agents.rag_agent import RAGAgent, DocumentQAAgent
import os
from datetime import datetime

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    collection_name: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload documents for RAG-based querying."""
    try:
        rag_agent = RAGAgent()
        
        # Use user-specific collection name
        coll_name = collection_name or f"user_{current_user.id}_docs"
        
        uploaded_docs = []
        documents = []
        metadatas = []
        
        for file in files:
            # Read file content
            content = await file.read()
            text_content = content.decode('utf-8')
            
            # Store in database
            doc = DocumentStore(
                user_id=current_user.id,
                filename=file.filename,
                content=text_content,
                content_type=file.content_type,
                collection_name=coll_name,
                file_size=len(content)
            )
            db.add(doc)
            
            documents.append(text_content)
            metadatas.append({
                "filename": file.filename,
                "upload_date": datetime.utcnow().isoformat()
            })
            
            uploaded_docs.append({
                "filename": file.filename,
                "size": len(content),
                "content_type": file.content_type
            })
        
        # Add documents to ChromaDB
        chunk_count = rag_agent.add_documents(coll_name, documents, metadatas)
        
        # Update chunk counts
        for doc in db.query(DocumentStore).filter(
            DocumentStore.user_id == current_user.id,
            DocumentStore.collection_name == coll_name,
            DocumentStore.chunk_count == 0
        ).all():
            doc.chunk_count = chunk_count // len(documents)
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Uploaded {len(files)} document(s)",
            "collection_name": coll_name,
            "documents": uploaded_docs,
            "total_chunks": chunk_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-documents")
async def get_my_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of user's uploaded documents."""
    docs = db.query(DocumentStore).filter(
        DocumentStore.user_id == current_user.id
    ).all()
    
    return {
        "status": "success",
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "collection_name": doc.collection_name,
                "chunk_count": doc.chunk_count,
                "file_size": doc.file_size,
                "uploaded_at": doc.uploaded_at.isoformat()
            }
            for doc in docs
        ]
    }


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a document."""
    doc = db.query(DocumentStore).filter(
        DocumentStore.id == doc_id,
        DocumentStore.user_id == current_user.id
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(doc)
    db.commit()
    
    return {
        "status": "success",
        "message": "Document deleted"
    }


@router.post("/query")
async def query_documents(
    query: str = Form(...),
    collection_name: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Query uploaded documents using RAG."""
    try:
        coll_name = collection_name or f"user_{current_user.id}_docs"
        
        # Check if user has documents
        doc_count = db.query(DocumentStore).filter(
            DocumentStore.user_id == current_user.id,
            DocumentStore.collection_name == coll_name
        ).count()
        
        if doc_count == 0:
            return {
                "status": "error",
                "message": "No documents found. Please upload documents first."
            }
        
        # Use DocumentQA agent
        agent = DocumentQAAgent()
        result = await agent.execute({
            "query": query,
            "collection_name": coll_name
        })
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
