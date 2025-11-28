import io
import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.agents.rag_agent import DocumentQAAgent, RAGAgent
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.agent_execution import DocumentStore
from app.models.user import User

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    collection_name: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Upload documents for RAG-based querying. Supports TXT, PDF, MD files."""
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

            # Extract text based on file type
            if file.filename.lower().endswith(".pdf"):
                # Extract text from PDF
                pdf_reader = PdfReader(io.BytesIO(content))
                text_content = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    text_content += f"\n--- Page {page_num + 1} ---\n"
                    text_content += page.extract_text()

                if not text_content.strip():
                    raise HTTPException(
                        status_code=400, detail=f"Could not extract text from {file.filename}"
                    )
            elif file.filename.lower().endswith((".txt", ".md", ".markdown")):
                # Plain text files
                text_content = content.decode("utf-8")
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.filename}. Supported types: PDF, TXT, MD",
                )

            # Store in database
            doc = DocumentStore(
                user_id=current_user.id,
                filename=file.filename,
                content=text_content[:10000],  # Store first 10k chars for preview
                content_type=file.content_type,
                collection_name=coll_name,
                file_size=len(content),
            )
            db.add(doc)

            documents.append(text_content)
            metadatas.append(
                {
                    "filename": file.filename,
                    "upload_date": datetime.utcnow().isoformat(),
                    "file_type": file.filename.split(".")[-1].upper(),
                    "pages": len(pdf_reader.pages) if file.filename.lower().endswith(".pdf") else 1,
                }
            )

            uploaded_docs.append(
                {
                    "filename": file.filename,
                    "size": len(content),
                    "content_type": file.content_type,
                    "text_length": len(text_content),
                    "pages": len(pdf_reader.pages) if file.filename.lower().endswith(".pdf") else 1,
                }
            )

        # Add documents to FAISS index
        chunk_count = rag_agent.add_documents(coll_name, documents, metadatas)

        # Update chunk counts
        chunks_per_doc = chunk_count // len(documents) if len(documents) > 0 else 0
        for doc in (
            db.query(DocumentStore)
            .filter(
                DocumentStore.user_id == current_user.id,
                DocumentStore.collection_name == coll_name,
                DocumentStore.chunk_count == 0,
            )
            .all()
        ):
            doc.chunk_count = chunks_per_doc

        db.commit()

        return {
            "status": "success",
            "message": f"Uploaded {len(files)} document(s) and created {chunk_count} searchable chunks",
            "collection_name": coll_name,
            "documents": uploaded_docs,
            "total_chunks": chunk_count,
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")


@router.get("/my-documents")
async def get_my_documents(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get list of user's uploaded documents."""
    docs = db.query(DocumentStore).filter(DocumentStore.user_id == current_user.id).all()

    return {
        "status": "success",
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "collection_name": doc.collection_name,
                "chunk_count": doc.chunk_count,
                "file_size": doc.file_size,
                "uploaded_at": doc.uploaded_at.isoformat(),
            }
            for doc in docs
        ],
    }


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a document."""
    doc = (
        db.query(DocumentStore)
        .filter(DocumentStore.id == doc_id, DocumentStore.user_id == current_user.id)
        .first()
    )

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(doc)
    db.commit()

    return {"status": "success", "message": "Document deleted"}


@router.post("/query")
async def query_documents(
    query: str = Form(...),
    collection_name: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Query uploaded documents using RAG."""
    try:
        coll_name = collection_name or f"user_{current_user.id}_docs"

        # Check if user has documents
        doc_count = (
            db.query(DocumentStore)
            .filter(
                DocumentStore.user_id == current_user.id, DocumentStore.collection_name == coll_name
            )
            .count()
        )

        if doc_count == 0:
            return {
                "status": "error",
                "message": "No documents found. Please upload documents first.",
            }

        # Use DocumentQA agent
        agent = DocumentQAAgent()
        result = await agent.execute({"query": query, "collection_name": coll_name})

        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
