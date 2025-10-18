# SPDX-License-Identifier: MIT
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any
import hashlib
import secrets
import base64

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from fastlib.config.manager import ConfigManager
from fastlib.schema import CurrentUser

# Configuration
security_config = ConfigManager.get_security_config()
server_config = ConfigManager.get_server_config()


def decode_jwt_token(token: str) -> dict[str, Any]:
    """Decode and validate JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        return jwt.decode(
            token,
            security_config.secret_key,
            algorithms=[security_config.algorithm],
        )
    except InvalidTokenError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token has expired. Please log in again.",
        ) from err
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials.",
        ) from err


def get_oauth2_scheme() -> OAuth2PasswordBearer:
    """Create OAuth2 password bearer scheme.
    
    Returns:
        OAuth2PasswordBearer instance
    """
    oauth2_scheme = OAuth2PasswordBearer(
        tokenUrl=f"{server_config.api_prefix}/v1/auth/auth:signInWithEmailAndPassword"
    )
    return oauth2_scheme


def get_current_user() -> Callable[[], CurrentUser]:
    """Get current user from access token.

    Returns:
        CurrentUser instance
    """

    def current_user(
        access_token: str = Depends(get_oauth2_scheme()),
    ) -> CurrentUser:
        if not security_config.enable:
            user_id = 9
            return CurrentUser(user_id=user_id)
        try:
            user_id = get_user_id(access_token)
        except InvalidTokenError as err:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your token has expired. Please log in again.",
            ) from err
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Error when decoding the token. Please check your request.",
            ) from err

        return CurrentUser(user_id=user_id)

    return current_user


def create_token(
    subject: str | int | None = None,
    expires_delta: timedelta | None = None,
    token_type: str | None = None,
) -> str:
    """Create new JWT token.

    Args:
        subject: Token subject (usually user ID)
        expires_delta: Optional timedelta for token expiration
        token_type: Token type identifier

    Returns:
        Encoded JWT string
    """
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=security_config.refresh_token_expire_minutes)
    )
    to_encode = {"exp": expire, "sub": str(subject), "type": token_type}
    return jwt.encode(
        to_encode,
        security_config.secret_key,
        algorithm=security_config.algorithm,
    )


def generate_salt(length: int = 16) -> str:
    """Generate a cryptographically secure random salt.
    
    Args:
        length: Length of the salt in bytes
        
    Returns:
        Base64 encoded salt string
    """
    return base64.b64encode(secrets.token_bytes(length)).decode('utf-8')


def hash_password_sha256(password: str, salt: str | None = None) -> tuple[str, str]:
    """Hash password using SHA-256 with salt.
    
    Args:
        password: Plain text password to hash
        salt: Salt for hashing. If None, generates random salt.
        
    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        salt = generate_salt()
    
    # Decode base64 salt
    salt_bytes = base64.b64decode(salt.encode('utf-8'))
    
    # Create hash with salt and password
    hash_obj = hashlib.sha256()
    hash_obj.update(salt_bytes + password.encode('utf-8'))
    
    # Multiple iterations for increased security (optional)
    for _ in range(1000):  # 1000 iterations
        hash_obj = hashlib.sha256(hash_obj.digest() + salt_bytes + password.encode('utf-8'))
    
    hashed_password = base64.b64encode(hash_obj.digest()).decode('utf-8')
    return hashed_password, salt


def verify_password(plain_password: str, hashed_password: str, salt: str | None = None) -> bool:
    """Verify password against hashed version using SHA-256.
    
    Args:
        plain_password: Input password to verify
        hashed_password: Stored hashed password
        salt: Salt used for the original hash. If None, uses a default salt.
        
    Returns:
        True if passwords match
    """
    try:
        # Use default salt if none provided (for backward compatibility)
        if salt is None:
            # Default salt - in production, this should be stored with the hash
            salt = "default_salt_placeholder"
        
        # Recalculate hash with the same salt and algorithm
        calculated_hash, _ = hash_password_sha256(plain_password, salt)
        
        # Use timing-safe comparison function
        return secrets.compare_digest(calculated_hash, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> tuple[str, str]:
    """Generate password hash using SHA-256.
    
    Args:
        password: Plain text password
        
    Returns:
        Tuple of (hashed_password, salt)
    """
    return hash_password_sha256(password)


def validate_token(token: str) -> bool:
    """Check if token is valid and not expired.

    Args:
        token: JWT token to validate

    Returns:
        True if token is valid

    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = decode_jwt_token(token)
        if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )
        return True
    except InvalidTokenError:
        return False


def get_user_id(token: str) -> int:
    """Extract user ID from JWT token.

    Args:
        token: JWT token string

    Returns:
        User ID extracted from the token

    Raises:
        HTTPException: If token is invalid or expired
    """
    payload = decode_jwt_token(token)
    return int(payload["sub"])


# Backward compatibility wrapper functions
def verify_password_compat(plain_password: str, hashed_password: str) -> bool:
    """Compatibility version of password verification with default salt.
    
    Args:
        plain_password: Input password to verify
        hashed_password: Stored hashed password
        
    Returns:
        True if passwords match
    """
    return verify_password(plain_password, hashed_password, salt=None)


def get_password_hash_compat(password: str) -> str:
    """Compatibility version of password hash function.
    
    Args:
        password: Plain text password
        
    Returns:
        Formatted string containing hash and salt (hash:salt)
    """
    hashed_password, salt = get_password_hash(password)
    return f"{hashed_password}:{salt}"


def parse_hashed_password(hashed_data: str) -> tuple[str, str]:
    """Parse hashed password data in format 'hash:salt'.
    
    Args:
        hashed_data: String containing hash and salt separated by colon
        
    Returns:
        Tuple of (hashed_password, salt)
        
    Raises:
        ValueError: If format is invalid
    """
    if ':' not in hashed_data:
        # If no salt is present, use default salt
        return hashed_data, "default_salt_placeholder"
    
    parts = hashed_data.split(':', 1)
    if len(parts) != 2:
        raise ValueError("Invalid hashed password format")
    
    return parts[0], parts[1]
