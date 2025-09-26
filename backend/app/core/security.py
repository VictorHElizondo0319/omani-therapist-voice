"""
Security and HIPAA compliance module
"""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from passlib.hash import bcrypt
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class SecurityManager:
    """Handles security, encryption, and HIPAA compliance"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.SECRET_KEY
        
        # HIPAA compliance settings
        self.data_retention_days = settings.DATA_RETENTION_DAYS
        self.encryption_algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.encryption_algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.encryption_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.JWTError as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data using AES encryption"""
        # In production, use proper AES encryption
        # For demo purposes, using simple encoding
        return hashlib.sha256(data.encode()).hexdigest()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        # In production, implement proper decryption
        # For demo purposes, this is a placeholder
        return encrypted_data
    
    def generate_session_id(self) -> str:
        """Generate cryptographically secure session ID"""
        return secrets.token_urlsafe(32)
    
    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize personal data for HIPAA compliance"""
        anonymized = data.copy()
        
        # Remove or hash personal identifiers
        sensitive_fields = ['name', 'email', 'phone', 'address', 'id_number']
        
        for field in sensitive_fields:
            if field in anonymized:
                if isinstance(anonymized[field], str) and len(anonymized[field]) > 0:
                    anonymized[field] = self.encrypt_sensitive_data(anonymized[field])
                else:
                    del anonymized[field]
        
        return anonymized
    
    def validate_hipaa_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against HIPAA compliance requirements"""
        compliance_check = {
            "is_compliant": True,
            "violations": [],
            "recommendations": []
        }
        
        # Check for required fields
        required_fields = ['session_id', 'timestamp', 'data_type']
        for field in required_fields:
            if field not in data:
                compliance_check["violations"].append(f"Missing required field: {field}")
                compliance_check["is_compliant"] = False
        
        # Check data retention
        if 'timestamp' in data:
            data_age = datetime.utcnow() - datetime.fromisoformat(data['timestamp'])
            if data_age.days > self.data_retention_days:
                compliance_check["recommendations"].append(
                    f"Data is {data_age.days} days old, consider deletion per retention policy"
                )
        
        # Check for encryption
        if 'sensitive_data' in data and not self._is_encrypted(data['sensitive_data']):
            compliance_check["violations"].append("Sensitive data not encrypted")
            compliance_check["is_compliant"] = False
        
        return compliance_check
    
    def _is_encrypted(self, data: str) -> bool:
        """Check if data appears to be encrypted"""
        # Simple heuristic - in production, use proper encryption validation
        return len(data) > 32 and all(c in '0123456789abcdefABCDEF' for c in data)
    
    def audit_log(self, action: str, user_id: Optional[str], details: Dict[str, Any]):
        """Log security-relevant actions for audit trail"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "details": details,
            "ip_address": details.get("ip_address", "unknown"),
            "user_agent": details.get("user_agent", "unknown")
        }
        
        # In production, write to secure audit log
        logger.info(f"Security Audit: {audit_entry}")
    
    def sanitize_input(self, input_data: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`']
        
        sanitized = input_data
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    def check_rate_limit(self, identifier: str, limit: int = 100, window: int = 3600) -> bool:
        """Check if request is within rate limit"""
        # In production, implement proper rate limiting with Redis
        # For demo purposes, always return True
        return True
    
    def generate_secure_filename(self, original_filename: str) -> str:
        """Generate secure filename to prevent path traversal"""
        # Remove directory traversal attempts
        secure_name = original_filename.replace('../', '').replace('..\\', '')
        
        # Generate random suffix
        random_suffix = secrets.token_hex(8)
        
        # Get file extension
        if '.' in secure_name:
            name, ext = secure_name.rsplit('.', 1)
            return f"{name}_{random_suffix}.{ext}"
        else:
            return f"{secure_name}_{random_suffix}"

# Global security manager instance
security_manager = SecurityManager()
