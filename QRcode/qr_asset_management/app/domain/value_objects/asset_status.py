"""
Asset Status Value Object
Enumeration for asset status
"""

from enum import Enum


class AssetStatus(Enum):
    """Asset status enumeration"""
    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"
    MAINTENANCE = "MAINTENANCE"
    DECOMMISSIONED = "DECOMMISSIONED"
    RESERVED = "RESERVED"

    @classmethod
    def choices(cls):
        """Get all status choices"""
        return [status.value for status in cls]

    @classmethod
    def from_string(cls, value: str) -> "AssetStatus":
        """Convert string to AssetStatus"""
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"Invalid status: {value}. Valid choices: {cls.choices()}")