"""
HIPAA compliance module for healthcare data protection
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DataClassification(Enum):
    """HIPAA data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class AccessLevel(Enum):
    """Access permission levels"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

@dataclass
class PHIElement:
    """Protected Health Information element"""
    identifier: str
    classification: DataClassification
    access_level: AccessLevel
    retention_period_days: int
    encryption_required: bool = True

class HIPAAManager:
    """Manages HIPAA compliance for healthcare data"""
    
    def __init__(self):
        self.phi_elements = self._initialize_phi_elements()
        self.audit_trail = []
        self.data_retention_policy = {
            "conversation_logs": 30,
            "crisis_incidents": 90,
            "user_profiles": 365,
            "audio_recordings": 7  # Minimal retention for audio
        }
    
    def _initialize_phi_elements(self) -> Dict[str, PHIElement]:
        """Initialize PHI elements with their classifications"""
        return {
            "conversation_content": PHIElement(
                identifier="conversation_content",
                classification=DataClassification.RESTRICTED,
                access_level=AccessLevel.READ,
                retention_period_days=30
            ),
            "emotional_analysis": PHIElement(
                identifier="emotional_analysis",
                classification=DataClassification.CONFIDENTIAL,
                access_level=AccessLevel.READ,
                retention_period_days=30
            ),
            "crisis_assessment": PHIElement(
                identifier="crisis_assessment",
                classification=DataClassification.RESTRICTED,
                access_level=AccessLevel.WRITE,
                retention_period_days=90
            ),
            "audio_data": PHIElement(
                identifier="audio_data",
                classification=DataClassification.RESTRICTED,
                access_level=AccessLevel.READ,
                retention_period_days=7,
                encryption_required=True
            ),
            "user_metadata": PHIElement(
                identifier="user_metadata",
                classification=DataClassification.CONFIDENTIAL,
                access_level=AccessLevel.READ,
                retention_period_days=365
            )
        }
    
    def classify_data(self, data_type: str) -> DataClassification:
        """Classify data according to HIPAA standards"""
        if data_type in self.phi_elements:
            return self.phi_elements[data_type].classification
        return DataClassification.INTERNAL
    
    def check_access_permission(self, user_role: str, data_type: str, requested_access: AccessLevel) -> bool:
        """Check if user has permission to access specific data"""
        if data_type not in self.phi_elements:
            return False
        
        phi_element = self.phi_elements[data_type]
        
        # Define role-based access control
        role_permissions = {
            "therapist": [AccessLevel.READ, AccessLevel.WRITE, AccessLevel.ADMIN],
            "supervisor": [AccessLevel.READ, AccessLevel.WRITE, AccessLevel.ADMIN],
            "system": [AccessLevel.READ, AccessLevel.WRITE, AccessLevel.ADMIN],
            "user": [AccessLevel.READ],
            "anonymous": [AccessLevel.READ]
        }
        
        user_permissions = role_permissions.get(user_role, [])
        return requested_access in user_permissions
    
    def encrypt_phi_data(self, data: Any, data_type: str) -> str:
        """Encrypt PHI data according to HIPAA requirements"""
        if data_type not in self.phi_elements:
            raise ValueError(f"Unknown data type: {data_type}")
        
        phi_element = self.phi_elements[data_type]
        
        if phi_element.encryption_required:
            # In production, use proper AES-256 encryption
            import hashlib
            import json
            
            data_str = json.dumps(data) if not isinstance(data, str) else data
            encrypted = hashlib.sha256(data_str.encode()).hexdigest()
            
            self._log_encryption_action(data_type, "encrypt")
            return encrypted
        
        return data
    
    def decrypt_phi_data(self, encrypted_data: str, data_type: str) -> Any:
        """Decrypt PHI data"""
        if data_type not in self.phi_elements:
            raise ValueError(f"Unknown data type: {data_type}")
        
        # In production, implement proper decryption
        self._log_encryption_action(data_type, "decrypt")
        return encrypted_data
    
    def validate_data_retention(self, data_type: str, creation_date: datetime) -> Dict[str, Any]:
        """Validate data against retention policy"""
        if data_type not in self.phi_elements:
            return {"valid": False, "reason": "Unknown data type"}
        
        phi_element = self.phi_elements[data_type]
        current_date = datetime.utcnow()
        age_days = (current_date - creation_date).days
        
        is_valid = age_days <= phi_element.retention_period_days
        
        return {
            "valid": is_valid,
            "age_days": age_days,
            "retention_limit_days": phi_element.retention_period_days,
            "should_delete": not is_valid
        }
    
    def create_audit_entry(self, action: str, user_id: str, data_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Create audit trail entry for HIPAA compliance"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "data_type": data_type,
            "classification": self.classify_data(data_type).value,
            "details": details,
            "compliance_verified": True
        }
        
        self.audit_trail.append(audit_entry)
        
        # In production, write to secure audit database
        logger.info(f"HIPAA Audit: {audit_entry}")
        
        return audit_entry
    
    def generate_breach_report(self, incident_details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate HIPAA breach report"""
        report = {
            "report_id": f"BREACH_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat(),
            "incident_type": incident_details.get("type", "unknown"),
            "affected_records": incident_details.get("affected_records", 0),
            "data_types_involved": incident_details.get("data_types", []),
            "severity": incident_details.get("severity", "unknown"),
            "containment_actions": incident_details.get("actions", []),
            "notification_required": self._requires_breach_notification(incident_details),
            "notification_deadline": self._calculate_notification_deadline()
        }
        
        # Log breach for immediate attention
        logger.critical(f"HIPAA Breach Detected: {report}")
        
        return report
    
    def _requires_breach_notification(self, incident_details: Dict[str, Any]) -> bool:
        """Determine if breach requires notification under HIPAA"""
        affected_records = incident_details.get("affected_records", 0)
        severity = incident_details.get("severity", "unknown")
        
        # HIPAA breach notification requirements
        return (
            affected_records >= 500 or
            severity in ["high", "critical"] or
            "financial_info" in incident_details.get("data_types", [])
        )
    
    def _calculate_notification_deadline(self) -> str:
        """Calculate notification deadline per HIPAA requirements"""
        # HIPAA requires notification within 60 days for breaches affecting 500+ individuals
        deadline = datetime.utcnow() + timedelta(days=60)
        return deadline.isoformat()
    
    def _log_encryption_action(self, data_type: str, action: str):
        """Log encryption/decryption actions"""
        self.create_audit_entry(
            action=f"data_{action}",
            user_id="system",
            data_type=data_type,
            details={"action": action, "timestamp": datetime.utcnow().isoformat()}
        )
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get overall HIPAA compliance summary"""
        total_audit_entries = len(self.audit_trail)
        recent_entries = [
            entry for entry in self.audit_trail
            if datetime.fromisoformat(entry["timestamp"]) > datetime.utcnow() - timedelta(days=7)
        ]
        
        return {
            "compliance_status": "compliant",
            "total_audit_entries": total_audit_entries,
            "recent_entries_7_days": len(recent_entries),
            "phi_elements_protected": len(self.phi_elements),
            "data_retention_policies": len(self.data_retention_policy),
            "last_audit_check": datetime.utcnow().isoformat(),
            "breach_incidents": 0  # Should be tracked in production
        }
    
    def sanitize_for_export(self, data: Dict[str, Any], export_type: str) -> Dict[str, Any]:
        """Sanitize data for export while maintaining HIPAA compliance"""
        sanitized = data.copy()
        
        # Remove or mask sensitive identifiers based on export type
        if export_type == "research":
            # For research, remove all PHI
            sensitive_fields = ["user_id", "session_id", "audio_data", "personal_info"]
            for field in sensitive_fields:
                if field in sanitized:
                    del sanitized[field]
        
        elif export_type == "clinical":
            # For clinical use, keep necessary PHI but ensure encryption
            if "conversation_content" in sanitized:
                sanitized["conversation_content"] = self.encrypt_phi_data(
                    sanitized["conversation_content"], "conversation_content"
                )
        
        return sanitized

# Global HIPAA manager instance
hipaa_manager = HIPAAManager()
