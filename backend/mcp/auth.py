"""
API Key Authentication for MCP Server
Manages and validates API keys for colleagues accessing the chatbot tools
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

# Path to store API keys
KEYS_FILE = Path(os.getenv("MCP_KEYS_FILE", "/vercel/share/v0-project/backend/mcp/keys.json"))


class APIKeyManager:
    """Manages API keys for MCP server access"""
    
    def __init__(self):
        self.keys_file = KEYS_FILE
        self.keys = self._load_keys()
    
    def _load_keys(self) -> Dict:
        """Load API keys from file"""
        if self.keys_file.exists():
            try:
                with open(self.keys_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading keys: {e}")
                return {}
        return {}
    
    def _save_keys(self):
        """Save API keys to file"""
        self.keys_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.keys_file, 'w') as f:
                json.dump(self.keys, f, indent=2, default=str)
            # Restrict file permissions
            os.chmod(self.keys_file, 0o600)
        except Exception as e:
            logger.error(f"Error saving keys: {e}")
    
    def generate_key(self, colleague_name: str, expires_in_days: Optional[int] = None) -> str:
        """
        Generate a new API key for a colleague
        
        Args:
            colleague_name: Name/email of the colleague
            expires_in_days: Days until key expires (None = no expiration)
            
        Returns:
            Generated API key
        """
        # Generate random key
        key = f"dnext_{secrets.token_urlsafe(32)}"
        
        # Hash for secure storage
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        # Metadata
        expiration = None
        if expires_in_days:
            expiration = (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat()
        
        self.keys[key_hash] = {
            "colleague": colleague_name,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expiration,
            "last_used": None,
            "usage_count": 0,
            "active": True
        }
        
        self._save_keys()
        logger.info(f"Generated API key for {colleague_name}")
        
        return key
    
    def validate_key(self, key: str) -> tuple[bool, Optional[Dict]]:
        """
        Validate an API key
        
        Args:
            key: API key to validate
            
        Returns:
            Tuple of (is_valid, key_info)
        """
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        if key_hash not in self.keys:
            logger.warning(f"Invalid key attempt: {key[:10]}...")
            return False, None
        
        key_info = self.keys[key_hash]
        
        # Check if active
        if not key_info.get("active"):
            logger.warning(f"Inactive key: {key_info['colleague']}")
            return False, None
        
        # Check expiration
        if key_info.get("expires_at"):
            expiration = datetime.fromisoformat(key_info["expires_at"])
            if datetime.utcnow() > expiration:
                logger.warning(f"Expired key: {key_info['colleague']}")
                return False, None
        
        # Update usage stats
        key_info["last_used"] = datetime.utcnow().isoformat()
        key_info["usage_count"] = key_info.get("usage_count", 0) + 1
        self._save_keys()
        
        logger.info(f"Valid key for {key_info['colleague']}")
        return True, key_info
    
    def revoke_key(self, key: str) -> bool:
        """Revoke an API key"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        if key_hash in self.keys:
            self.keys[key_hash]["active"] = False
            self._save_keys()
            logger.info(f"Revoked key: {self.keys[key_hash]['colleague']}")
            return True
        
        return False
    
    def list_keys(self) -> List[Dict]:
        """List all active API keys (for admin purposes)"""
        return [
            {
                "colleague": info["colleague"],
                "created_at": info["created_at"],
                "expires_at": info["expires_at"],
                "last_used": info["last_used"],
                "usage_count": info["usage_count"],
                "active": info["active"]
            }
            for info in self.keys.values()
        ]
    
    def get_key_info(self, key: str) -> Optional[Dict]:
        """Get info about a specific key (without exposing hash)"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        if key_hash in self.keys:
            return {
                "colleague": self.keys[key_hash]["colleague"],
                "created_at": self.keys[key_hash]["created_at"],
                "expires_at": self.keys[key_hash]["expires_at"],
                "last_used": self.keys[key_hash]["last_used"],
                "usage_count": self.keys[key_hash]["usage_count"],
                "active": self.keys[key_hash]["active"]
            }
        
        return None


# Global key manager instance
key_manager = APIKeyManager()


def validate_api_key(auth_header: Optional[str]) -> tuple[bool, Optional[Dict]]:
    """
    Validate API key from Authorization header
    
    Expected format: "Bearer dnext_xxxxx"
    """
    if not auth_header:
        return False, None
    
    try:
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != "Bearer":
            return False, None
        
        key = parts[1]
        return key_manager.validate_key(key)
    
    except Exception as e:
        logger.error(f"Error validating key: {e}")
        return False, None
