from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseDataSource(ABC):
    """Abstract base class for consumption data sources."""
    
    @abstractmethod
    def get_consumption_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Get consumption data for the specified date range.
        
        Args:
            start_date: Start date in ISO format (e.g., "2025-01-07T00:00:00Z")
            end_date: End date in ISO format (e.g., "2025-01-07T23:59:59Z")
            
        Returns:
            List of consumption records with format:
            [
                {
                    'readAt': '2025-01-07T10:30:00Z',
                    'consumptionDelta': 500,  # Wh for the period
                    'costDeltaWithTax': 12.5  # Cost in pence including VAT
                },
                ...
            ]
        """
        pass
    
    @abstractmethod
    def get_standing_charge(self) -> float:
        """
        Get the current standing charge in pence per day.
        
        Returns:
            Standing charge in pence
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this data source is available and properly configured.
        
        Returns:
            True if the data source can be used, False otherwise
        """
        pass
