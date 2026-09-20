from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timedelta
import secrets
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.password_reset import PasswordResetToken
from app.utils.auth import PasswordManager, SessionManager, login_rate_limiter
from app.models import AuditLog

# OAuth2 scheme for FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
security = HTTPBearer()


router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Pydantic models
class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime]


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse


async def get_current_user(credentials=Depends(security), db: Session = Depends(get_db)) -> User:
    """Get the authenticated user from a bearer token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = SessionManager.validate_session(credentials.credentials)
    if not payload or not payload.get("sub"):
        raise credentials_exception

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")
    return user


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account"""
    # Validate password confirmation
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Validate password strength
    is_valid, message = PasswordManager.validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_id = secrets.token_urlsafe(36)
    password_hash = PasswordManager.hash_password(user_data.password)
    
    new_user = User(
        id=user_id,
        name=user_data.name,
        email=user_data.email,
        password_hash=password_hash,
        role=UserRole.USER,
        is_active=True
    )
    
    db.add(new_user)
    
    # Create audit log
    audit_log = AuditLog(
        id=secrets.token_urlsafe(36),
        user_id=user_id,
        action="USER_CREATED",
        target_type="USER",
        target_id=user_id,
        metadata_json={"email": user_data.email, "name": user_data.name}
    )
    db.add(audit_log)
    
    db.commit()
    db.refresh(new_user)
    
    # Create session
    session_data = SessionManager.create_session(user_id, {
        "sub": user_id,
        "role": new_user.role.value,
        "name": new_user.name
    })
    
    # Update last login
    new_user.last_login_at = datetime.utcnow()
    db.commit()
    
    return TokenResponse(
        **session_data,
        user=UserResponse(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
            role=new_user.role.value,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            last_login_at=new_user.last_login_at
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    # Rate limiting
    if not login_rate_limiter.is_allowed(login_data.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Find user
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user:
        login_rate_limiter.record_attempt(login_data.email, False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        login_rate_limiter.record_attempt(login_data.email, False)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Verify password
    if not PasswordManager.verify_password(login_data.password, user.password_hash):
        login_rate_limiter.record_attempt(login_data.email, False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Record successful attempt
    login_rate_limiter.record_attempt(login_data.email, True)
    
    # Create session
    session_data = SessionManager.create_session(user.id, {
        "sub": user.id,
        "role": user.role.value,
        "name": user.name
    })
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    
    # Create audit log
    audit_log = AuditLog(
        id=secrets.token_urlsafe(36),
        user_id=user.id,
        action="LOGIN",
        target_type="USER",
        target_id=user.id
    )
    db.add(audit_log)
    
    db.commit()
    db.refresh(user)
    
    return TokenResponse(
        **session_data,
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout user"""
    # Create audit log
    audit_log = AuditLog(
        id=secrets.token_urlsafe(36),
        user_id=current_user.id,
        action="LOGOUT",
        target_type="USER",
        target_id=current_user.id
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Successfully logged out"}


@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    """Request password reset"""
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        # Don't reveal whether email exists
        return {"message": "If an account exists with this email, a password reset link will be sent."}
    
    # Create reset token
    token = secrets.token_urlsafe(32)
    token_hash = PasswordManager.hash_password(token)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    reset_token = PasswordResetToken(
        id=secrets.token_urlsafe(36),
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    
    db.add(reset_token)
    db.commit()
    
    # In production, send email with reset link
    # For now, return the token (for development only)
    return {
        "message": "Password reset link sent to email",
        "reset_token": token  # Remove this in production
    }


@router.post("/reset-password")
async def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    """Reset password with token"""
    # Validate password confirmation
    if data.new_password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Validate password strength
    is_valid, message = PasswordManager.validate_password_strength(data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Find reset token
    token_hash = PasswordManager.hash_password(data.token)
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.used_at == None,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get user
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.password_hash = PasswordManager.hash_password(data.new_password)
    
    # Mark token as used
    reset_token.used_at = datetime.utcnow()
    
    # Create audit log
    audit_log = AuditLog(
        id=secrets.token_urlsafe(36),
        user_id=user.id,
        action="PASSWORD_RESET",
        target_type="USER",
        target_id=user.id
    )
    db.add(audit_log)
    
    db.commit()
    
    return {"message": "Password successfully reset"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
    )


@router.patch("/profile")
async def update_profile(
    name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    if name:
        current_user.name = name
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
    )


@router.post("/change-password")
async def change_password(
    data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Validate password confirmation
    if data.new_password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
    )
    
    # Validate password strength
    is_valid, message = PasswordManager.validate_password_strength(data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Verify current password
    if not PasswordManager.verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = PasswordManager.hash_password(data.new_password)
    current_user.updated_at = datetime.utcnow()
    
    # Create audit log
    audit_log = AuditLog(
        id=secrets.token_urlsafe(36),
        user_id=current_user.id,
        action="PASSWORD_CHANGED",
        target_type="USER",
        target_id=current_user.id
    )
    db.add(audit_log)
    
    db.commit()
    
    return {"message": "Password successfully changed"}


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify they are an admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
