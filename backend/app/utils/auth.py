import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from app.config import settings


class PasswordManager:
    """Handle password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """Validate password strength requirements"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"


class TokenManager:
    """Handle JWT token generation and validation"""
    
    SECRET_KEY = settings.secret_key if hasattr(settings, 'secret_key') else secrets.token_urlsafe(32)
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    @classmethod
    def create_access_token(cls, data: Dict[str, Any]) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
    
    @classmethod
    def create_refresh_token(cls, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
    
    @classmethod
    def decode_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


class SessionManager:
    """Manage user sessions"""
    
    @staticmethod
    def create_session(user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new session"""
        access_token = TokenManager.create_access_token({
            "sub": user_id,
            "role": user_data.get("role"),
            "name": user_data.get("name")
        })
        
        refresh_token = TokenManager.create_refresh_token({
            "sub": user_id
        })
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    @staticmethod
    def validate_session(token: str) -> Optional[Dict[str, Any]]:
        """Validate a session token"""
        payload = TokenManager.decode_token(token)
        if payload and payload.get("type") == "access":
            return payload
        return None


class RateLimiter:
    """Simple rate limiting for login attempts"""
    
    def __init__(self):
        self.attempts = {}  # {ip_or_email: [(timestamp, success)]}
        self.max_attempts = 5
        self.window_minutes = 15
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if the identifier is allowed to attempt login"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.window_minutes)
        
        # Clean old attempts
        if identifier in self.attempts:
            self.attempts[identifier] = [
                (ts, success) for ts, success in self.attempts[identifier]
                if ts > window_start
            ]
        
        # Count failed attempts in window
        failed_attempts = sum(1 for ts, success in self.attempts.get(identifier, []) if not success and ts > window_start)
        
        return failed_attempts < self.max_attempts
    
    def record_attempt(self, identifier: str, success: bool):
        """Record a login attempt"""
        if identifier not in self.attempts:
            self.attempts[identifier] = []
        
        self.attempts[identifier].append((datetime.utcnow(), success))
        
        # Clean old attempts
        window_start = datetime.utcnow() - timedelta(minutes=self.window_minutes)
        self.attempts[identifier] = [
            (ts, success) for ts, success in self.attempts[identifier]
            if ts > window_start
        ]


# Global rate limiter instance
login_rate_limiter = RateLimiter()
