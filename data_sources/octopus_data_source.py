from typing import List, Dict, Any
from .base_data_source import BaseDataSource
from queries import consumption_query
import config


class OctopusDataSource(BaseDataSource):
    """Data source that uses Octopus Energy GraphQL API (current implementation)."""
    
    def __init__(self, query_service, device_id: str, current_standing_charge: float):
        self.query_service = query_service
        self.device_id = device_id
        self.current_standing_charge = current_standing_charge
    
    def get_consumption_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get consumption data from Octopus Energy GraphQL API."""
        query = consumption_query.format(
            device_id=self.device_id,
            start_date=start_date,
            end_date=end_date
        )
        result = self.query_service.execute_gql_query(query)
        return result['smartMeterTelemetry']
    
    def get_standing_charge(self) -> float:
        """Get the current standing charge from account info."""
        return self.current_standing_charge
    
    def is_available(self) -> bool:
        """Check if Octopus API is available."""
        return (
            self.query_service is not None and
            self.device_id is not None and
            config.API_KEY and
            config.ACC_NUMBER
        )
