"""
Access Key Model

Represents an API access key with module-based permissions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from pravaha.domain.auth.model.module import PravahaModule


@dataclass
class AccessKey:
    """
    Application access key model.
    
    Represents an API access key for application-level authentication
    with module-based permissions.
    
    Attributes:
        id: Unique identifier (UUID)
        key: The actual API key (stored as hash)
        name: Human-readable name (e.g., "Production App")
        created_at: When the key was created
        permissions: List of modules this key can access
        last_used: Last time the key was used
        is_active: Whether the key is active or revoked
        description: Optional description of the key's purpose
    """
    
    id: str
    key: str  # Hashed in storage
    name: str
    created_at: datetime
    permissions: List[PravahaModule] = field(default_factory=list)
    last_used: Optional[datetime] = None
    is_active: bool = True
    description: Optional[str] = None
    
    def has_permission(self, module: PravahaModule) -> bool:
        """
        Check if this key has permission for a specific module.
        
        Args:
            module: The module to check permission for
            
        Returns:
            True if key has permission, False otherwise
        """
        return module in self.permissions
    
    def has_all_permissions(self, modules: List[PravahaModule]) -> bool:
        """
        Check if this key has all specified permissions.
        
        Args:
            modules: List of modules to check
            
        Returns:
            True if key has all permissions, False otherwise
        """
        return all(m in self.permissions for m in modules)
    
    def has_any_permission(self, modules: List[PravahaModule]) -> bool:
        """
        Check if this key has any of the specified permissions.
        
        Args:
            modules: List of modules to check
            
        Returns:
            True if key has at least one permission, False otherwise
        """
        return any(m in self.permissions for m in modules)
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary for JSON storage.
        
        Returns:
            Dictionary representation of the access key
        """
        return {
            "id": self.id,
            "key": self.key,  # Should be hashed
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "permissions": [p.value for p in self.permissions],
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "is_active": self.is_active,
            "description": self.description
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'AccessKey':
        """
        Create AccessKey from dictionary (JSON deserialization).
        
        Args:
            data: Dictionary containing access key data
            
        Returns:
            AccessKey instance
        """
        return AccessKey(
            id=data["id"],
            key=data["key"],
            name=data["name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            permissions=[PravahaModule(p) for p in data.get("permissions", [])],
            last_used=datetime.fromisoformat(data["last_used"]) if data.get("last_used") else None,
            is_active=data.get("is_active", True),
            description=data.get("description")
        )
