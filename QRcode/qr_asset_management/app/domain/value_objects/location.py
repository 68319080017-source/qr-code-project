"""
Location Value Object
Immutable value object for asset location
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    """
    Location value object
    Immutable representation of asset location
    """
    building: str
    floor: Optional[str] = None
    room: Optional[str] = None
    shelf: Optional[str] = None
    description: Optional[str] = None

    @property
    def full_address(self) -> str:
        """Get full location address"""
        parts = [self.building]
        if self.floor:
            parts.append(f"Floor {self.floor}")
        if self.room:
            parts.append(f"Room {self.room}")
        if self.shelf:
            parts.append(f"Shelf {self.shelf}")
        return ", ".join(parts)

    @property
    def short_address(self) -> str:
        """Get short location address"""
        if self.room:
            return f"{self.building} - {self.room}"
        return self.building