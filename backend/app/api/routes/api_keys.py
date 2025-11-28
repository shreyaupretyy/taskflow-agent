import secrets
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, get_password_hash
from app.models.api_key import APIKey
from app.models.user import User
from app.schemas.api_key import APIKeyCreate, APIKeyResponse, APIKeyWithSecret

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


def generate_api_key() -> tuple[str, str, str]:
    """Generate a new API key."""
    key = f"tk_{secrets.token_urlsafe(32)}"
    key_prefix = key[:11]  # tk_ + 8 chars
    key_hash = get_password_hash(key)
    return key, key_prefix, key_hash


@router.post("", response_model=APIKeyWithSecret, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new API key."""
    key, key_prefix, key_hash = generate_api_key()

    api_key = APIKey(
        user_id=current_user.id,
        name=api_key_data.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        expires_at=api_key_data.expires_at,
        is_active=True,
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    # Return the key only once
    return {**api_key.__dict__, "key": key}


@router.get("", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """List all API keys for the current user."""
    api_keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()

    return api_keys


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete an API key."""
    api_key = (
        db.query(APIKey).filter(APIKey.id == api_key_id, APIKey.user_id == current_user.id).first()
    )

    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

    db.delete(api_key)
    db.commit()

    return None


@router.patch("/{api_key_id}/deactivate", response_model=APIKeyResponse)
async def deactivate_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Deactivate an API key."""
    api_key = (
        db.query(APIKey).filter(APIKey.id == api_key_id, APIKey.user_id == current_user.id).first()
    )

    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

    api_key.is_active = False
    db.commit()
    db.refresh(api_key)

    return api_key
