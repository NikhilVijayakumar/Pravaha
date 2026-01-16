"""
Access Key Repository Protocol

Protocol for access key storage backends with permission support.
"""

from typing import Protocol, List, Optional
from pravaha.domain.auth.model.access_key import AccessKey
from pravaha.domain.auth.model.module import PravahaModule


class AccessKeyRepositoryProtocol(Protocol):
    """
    Protocol for access key storage backends.
    
    Clients can implement this protocol to use custom storage
    (PostgreSQL, MongoDB, Redis, etc.) for access keys.
    """
    
    def validate_key(self, key: str) -> bool:
        """
        Validate if an API key is valid and active.
        
        Args:
            key: The API key to validate (unhashed)
            
        Returns:
            True if key is valid and active, False otherwise
        """
        ...
    
    def get_key_by_value(self, key: str) -> Optional[AccessKey]:
        """
        Get access key details by key value.
        
        Args:
            key: The API key value (unhashed)
            
        Returns:
            AccessKey if found and active, None otherwise
        """
        ...
    
    def create_key(
        self, 
        name: str, 
        description: Optional[str] = None,
        permissions: Optional[List[PravahaModule]] = None
    ) -> AccessKey:
        """
        Create a new API access key with specified permissions.
        
        Args:
            name: Human-readable name for the key
            description: Optional description
            permissions: List of modules this key can access (default: all)
            
        Returns:
            Created AccessKey with generated key value (unhashed, shown only once)
        """
        ...
    
    def revoke_key(self, key_id: str) -> None:
        """
        Revoke (deactivate) an API key.
        
        Args:
            key_id: The ID of the key to revoke
        """
        ...
    
    def list_keys(self, include_inactive: bool = False) -> List[AccessKey]:
        """
        List all API keys.
        
        Args:
            include_inactive: Whether to include revoked keys
            
        Returns:
            List of AccessKey objects (key values are masked)
        """
        ...
    
    def update_last_used(self, key_id: str) -> None:
        """
        Update the last_used timestamp for a key.
        
        Args:
            key_id: The ID of the key
        """
        ...
    
    def get_key_by_id(self, key_id: str) -> Optional[AccessKey]:
        """
        Get access key by ID.
        
        Args:
            key_id: The key ID
            
        Returns:
            AccessKey if found, None otherwise
        """
        ...
