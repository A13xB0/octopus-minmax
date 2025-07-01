from typing import Optional
import config
from .base_data_source import BaseDataSource
from .octopus_data_source import OctopusDataSource
from .home_assistant_data_source import HomeAssistantDataSource
from notification import send_notification


class DataSourceFactory:
    """Factory class to create the appropriate data source based on configuration."""
    
    @staticmethod
    def create_data_source(query_service=None, device_id: str = None, current_standing_charge: float = None) -> BaseDataSource:
        """
        Create and return the appropriate data source based on configuration.
        
        Args:
            query_service: Octopus GraphQL query service (for Octopus data source)
            device_id: Octopus device ID (for Octopus data source)
            current_standing_charge: Current standing charge from Octopus (for Octopus data source)
            
        Returns:
            BaseDataSource: The configured data source
            
        Raises:
            Exception: If no valid data source can be created
        """
        # Check if Home Assistant configuration is provided
        if hasattr(config, 'HA_ENERGY_ENTITY') and config.HA_ENERGY_ENTITY:
            ha_data_source = HomeAssistantDataSource()
            if ha_data_source.is_available():
                print("Using Home Assistant data source")
                return ha_data_source
            else:
                print("Home Assistant configuration incomplete, falling back to Octopus")
        
        # Fall back to Octopus data source
        if query_service and device_id is not None and current_standing_charge is not None:
            octopus_data_source = OctopusDataSource(query_service, device_id, current_standing_charge)
            if octopus_data_source.is_available():
                print("Using Octopus Energy data source")
                return octopus_data_source
        
        raise Exception("No valid data source available. Please check your configuration.")
    
    @staticmethod
    def get_data_source_info() -> dict:
        """
        Get information about which data source would be used.
        
        Returns:
            dict: Information about the data source selection
        """
        info = {
            "ha_configured": False,
            "ha_available": False,
            "octopus_available": False,
            "selected_source": None
        }
        
        # Check Home Assistant configuration
        if hasattr(config, 'HA_ENERGY_ENTITY') and config.HA_ENERGY_ENTITY:
            info["ha_configured"] = True
            ha_data_source = HomeAssistantDataSource()
            info["ha_available"] = ha_data_source.is_available()
            
            if info["ha_available"]:
                info["selected_source"] = "home_assistant"
                return info
        
        # Check Octopus configuration
        info["octopus_available"] = bool(config.API_KEY and config.ACC_NUMBER)
        if info["octopus_available"]:
            info["selected_source"] = "octopus"
        
        return info
