"""
JSON Access Key Repository

Default JSON file-based implementation of AccessKeyRepositoryProtocol.
"""

import json
import secrets
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import uuid

from pravaha.domain.auth.model.access_key import AccessKey
from pravaha.domain.auth.model.module import PravahaModule
from pravaha.domain.auth.protocol.access_key_repository_protocol import AccessKeyRepositoryProtocol
from pravaha.domain.config.cache_config import CachePathConfig


class JsonAccessKeyRepository(AccessKeyRepositoryProtocol):
    """
    JSON file-based access key repository.
    
    Default implementation storing keys in JSON file with hashed values.
    Supports module-based permissions.
    """
    
    def __init__(self, cache_config: Optional[CachePathConfig] = None):
        """
        Initialize JSON repository.
        
        Args:
            cache_config: Cache configuration for storage location
        """
        if cache_config is None:
            cache_config = CachePathConfig.default()
        
        self.config_dir = Path.cwd() / cache_config.cache_root / "auth"
        self.keys_file = self.config_dir / "access_keys.json"
        
        # Ensure directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize file if doesn't exist
        if not self.keys_file.exists():
            self._save_keys([])
    
    def _hash_key(self, key: str) -> str:
        """
        Hash an API key for secure storage.
        
        Args:
            key: The unhashed API key
            
        Returns:
            SHA-256 hash of the key
        """
        return hashlib.sha256(key.encode()).hexdigest()
    
    def _generate_key(self) -> str:
        """
        Generate a secure random API key.
        
        Returns:
            URL-safe random string (32 bytes)
        """
        return secrets.token_urlsafe(32)
    
    def _load_keys(self) -> List[AccessKey]:
        """
        Load all keys from JSON file.
        
        Returns:
            List of AccessKey objects
        """
        with open(self.keys_file, 'r') as f:
            data = json.load(f)
        return [AccessKey.from_dict(key_data) for key_data in data]
    
    def _save_keys(self, keys: List[AccessKey]) -> None:
        """
        Save keys to JSON file.
        
        Args:
            keys: List of AccessKey objects to save
        """
        with open(self.keys_file, 'w') as f:
            json.dump([key.to_dict() for key in keys], f, indent=2)
    
    def _find_key_by_hash(self, hashed: str) -> Optional[AccessKey]:
        """
        Find key by hashed value.
        
        Args:
            hashed: Hashed key value
            
        Returns:
            AccessKey if found, None otherwise
        """
        keys = self._load_keys()
        for key in keys:
            if key.key == hashed:
                return key
        return None
    
    def validate_key(self, key: str) -> bool:
        """Validate API key."""
        hashed = self._hash_key(key)
        stored_key = self._find_key_by_hash(hashed)
        
        if stored_key and stored_key.is_active:
            # Update last used
            self.update_last_used(stored_key.id)
            return True
        
        return False
    
    def get_key_by_value(self, key: str) -> Optional[AccessKey]:
        """Get key by value."""
        hashed = self._hash_key(key)
        stored_key = self._find_key_by_hash(hashed)
        
        if stored_key and stored_key.is_active:
            return stored_key
        
        return None
    
    def create_key(
        self, 
        name: str,
        description: Optional[str] = None,
        permissions: Optional[List[PravahaModule]] = None
    ) -> AccessKey:
        """Create new API key with permissions."""
        # Generate raw key (to return to user)
        raw_key = self._generate_key()
        hashed_key = self._hash_key(raw_key)
        
        # Default to all permissions if none specified
        if permissions is None:
            permissions = PravahaModule.all_modules()
        
        # Create access key object
        access_key = AccessKey(
            id=str(uuid.uuid4()),
            key=hashed_key,  # Store hashed version
            name=name,
            created_at=datetime.now(),
            permissions=permissions,
            description=description
        )
        
        # Load existing keys
        keys = self._load_keys()
        keys.append(access_key)
        self._save_keys(keys)
        
        # Return copy with raw key (only time it's visible)
        access_key_with_raw = AccessKey(
            id=access_key.id,
            key=raw_key,  # Return unhashed for user to save
            name=access_key.name,
            created_at=access_key.created_at,
            permissions=access_key.permissions,
            description=access_key.description
        )
        
        return access_key_with_raw
    
    def revoke_key(self, key_id: str) -> None:
        """Revoke API key."""
        keys = self._load_keys()
        
        for key in keys:
            if key.id == key_id:
                key.is_active = False
                break
        
        self._save_keys(keys)
    
    def list_keys(self, include_inactive: bool = False) -> List[AccessKey]:
        """List all keys."""
        keys = self._load_keys()
        
        if not include_inactive:
            keys = [k for k in keys if k.is_active]
        
        # Don't expose actual key values
        for key in keys:
            key.key = "***HIDDEN***"
        
        return keys
    
    def update_last_used(self, key_id: str) -> None:
        """Update last used timestamp."""
        keys = self._load_keys()
        
        for key in keys:
            if key.id == key_id:
                key.last_used = datetime.now()
                break
        
        self._save_keys(keys)
    
    def get_key_by_id(self, key_id: str) -> Optional[AccessKey]:
        """Get key by ID."""
        keys = self._load_keys()
        
        for key in keys:
            if key.id == key_id:
                # Mask the key value
                key.key = "***HIDDEN***"
                return key
        
        return None
