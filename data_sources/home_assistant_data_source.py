from typing import List, Dict, Any
from datetime import datetime, timedelta
import requests
import config
from .base_data_source import BaseDataSource


class HomeAssistantDataSource(BaseDataSource):
    """Data source that uses Home Assistant API with Shelly and Octopus Energy entities."""
    
    def __init__(self):
        self.ha_url = config.HA_URL or "http://supervisor/core/api"
        self.ha_token = config.HA_TOKEN
        self.energy_entity = config.HA_ENERGY_ENTITY
        self.rate_entity = config.HA_RATE_ENTITY
        self.standing_charge_entity = config.HA_STANDING_CHARGE_ENTITY
        
        self.headers = {
            "Authorization": f"Bearer {self.ha_token}",
            "Content-Type": "application/json"
        }
    
    def get_consumption_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get consumption data from Home Assistant."""
        try:
            # Get energy history data
            energy_history = self._get_entity_history(self.energy_entity, start_date, end_date)
            
            # Get rate history data
            rate_history = self._get_entity_history(self.rate_entity, start_date, end_date)
            
            # Process data into 30-minute intervals
            consumption_data = self._process_consumption_data(energy_history, rate_history)
            
            return consumption_data
            
        except Exception as e:
            raise Exception(f"Failed to get consumption data from Home Assistant: {e}")
    
    def get_standing_charge(self) -> float:
        """Get the current standing charge from Home Assistant."""
        try:
            response = requests.get(
                f"{self.ha_url}/states/{self.standing_charge_entity}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            standing_charge_pounds = float(data['state'])
            
            # Convert from pounds to pence
            return standing_charge_pounds * 100
            
        except Exception as e:
            raise Exception(f"Failed to get standing charge from Home Assistant: {e}")
    
    def is_available(self) -> bool:
        """Check if Home Assistant integration is properly configured."""
        return all([
            self.ha_token,
            self.energy_entity,
            self.rate_entity,
            self.standing_charge_entity
        ])
    
    def _get_entity_history(self, entity_id: str, start_date: str, end_date: str) -> List[Dict]:
        """Get historical data for an entity from Home Assistant."""
        # Convert ISO dates to HA format if needed
        start_timestamp = start_date.replace('Z', '+00:00')
        end_timestamp = end_date.replace('Z', '+00:00')
        
        url = f"{self.ha_url}/history/period/{start_timestamp}"
        params = {
            "filter_entity_id": entity_id,
            "end_time": end_timestamp,
            "minimal_response": "true"
        }
        
        response = requests.get(url, headers=self.headers, params=params, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        if not data or not data[0]:
            return []
        
        return data[0]  # HA returns array of arrays, we want the first entity's data
    
    def _process_consumption_data(self, energy_history: List[Dict], rate_history: List[Dict]) -> List[Dict[str, Any]]:
        """Process energy and rate history into 30-minute consumption periods."""
        consumption_data = []
        
        if not energy_history:
            return consumption_data
        
        # Sort by timestamp
        energy_history.sort(key=lambda x: x['last_changed'])
        rate_history.sort(key=lambda x: x['last_changed'])
        
        # Generate 30-minute intervals for today
        start_time = datetime.fromisoformat(energy_history[0]['last_changed'].replace('Z', '+00:00'))
        start_time = start_time.replace(minute=0 if start_time.minute < 30 else 30, second=0, microsecond=0)
        
        current_time = start_time
        end_time = datetime.now().replace(tzinfo=start_time.tzinfo)
        
        prev_energy = None
        
        while current_time < end_time:
            period_end = current_time + timedelta(minutes=30)
            
            # Get energy reading at the end of this period
            energy_reading = self._get_reading_at_time(energy_history, period_end.isoformat())
            
            if energy_reading is not None and prev_energy is not None:
                # Calculate consumption delta in Wh
                energy_kwh = float(energy_reading)
                prev_energy_kwh = float(prev_energy)
                consumption_delta_kwh = max(0, energy_kwh - prev_energy_kwh)
                consumption_delta_wh = consumption_delta_kwh * 1000
                
                # Get rate for this period
                rate_reading = self._get_reading_at_time(rate_history, current_time.isoformat())
                
                if rate_reading is not None:
                    rate_pounds_per_kwh = float(rate_reading)
                    # Calculate cost: consumption_kwh * rate * VAT * 100 (to get pence)
                    cost_delta_with_tax = consumption_delta_kwh * rate_pounds_per_kwh * 1.05 * 100
                    
                    consumption_data.append({
                        'readAt': period_end.strftime('%Y-%m-%dT%H:%M:%S') + 'Z',
                        'consumptionDelta': consumption_delta_wh,
                        'costDeltaWithTax': cost_delta_with_tax
                    })
            
            prev_energy = energy_reading
            current_time = period_end
        
        return consumption_data
    
    def _get_reading_at_time(self, history: List[Dict], target_time: str) -> float:
        """Get the reading closest to the target time."""
        if not history:
            return None
        
        target_dt = datetime.fromisoformat(target_time.replace('Z', '+00:00'))
        
        # Find the reading closest to but not after the target time
        best_reading = None
        best_time_diff = None
        
        for reading in history:
            reading_time = datetime.fromisoformat(reading['last_changed'].replace('Z', '+00:00'))
            
            if reading_time <= target_dt:
                time_diff = (target_dt - reading_time).total_seconds()
                
                if best_time_diff is None or time_diff < best_time_diff:
                    best_time_diff = time_diff
                    best_reading = reading['state']
        
        return best_reading
