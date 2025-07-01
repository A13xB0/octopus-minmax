#!/usr/bin/env python3
"""
Test script for Home Assistant integration with Octopus MinMax Bot.
This script helps verify that your HA entities are configured correctly.
"""

import os
import sys
import traceback
from datetime import date
from data_sources.home_assistant_data_source import HomeAssistantDataSource
from data_sources.data_source_factory import DataSourceFactory
import config


def test_ha_configuration():
    """Test Home Assistant configuration and entity availability."""
    print("🏠 Testing Home Assistant Integration")
    print("=" * 50)
    
    # Check configuration
    print("📋 Configuration Check:")
    print(f"  HA_URL: {config.HA_URL or 'Not set (will use default)'}")
    print(f"  HA_TOKEN: {'✅ Set' if config.HA_TOKEN else '❌ Not set'}")
    print(f"  HA_ENERGY_ENTITY: {config.HA_ENERGY_ENTITY or '❌ Not set'}")
    print(f"  HA_RATE_ENTITY: {config.HA_RATE_ENTITY or '❌ Not set'}")
    print(f"  HA_STANDING_CHARGE_ENTITY: {config.HA_STANDING_CHARGE_ENTITY or '❌ Not set'}")
    print()
    
    if not config.HA_ENERGY_ENTITY:
        print("❌ HA_ENERGY_ENTITY is required for Home Assistant integration")
        return False
    
    if not config.HA_TOKEN:
        print("❌ HA_TOKEN is required for Home Assistant integration")
        return False
    
    if not config.HA_RATE_ENTITY:
        print("❌ HA_RATE_ENTITY is required for cost calculation")
        return False
    
    if not config.HA_STANDING_CHARGE_ENTITY:
        print("❌ HA_STANDING_CHARGE_ENTITY is required for cost calculation")
        return False
    
    # Test data source creation
    print("🔧 Testing Data Source Creation:")
    try:
        ha_source = HomeAssistantDataSource()
        if ha_source.is_available():
            print("  ✅ Home Assistant data source created successfully")
        else:
            print("  ❌ Home Assistant data source not available")
            return False
    except Exception as e:
        print(f"  ❌ Failed to create HA data source: {e}")
        return False
    
    # Test standing charge
    print("\n💰 Testing Standing Charge:")
    try:
        standing_charge = ha_source.get_standing_charge()
        print(f"  ✅ Standing charge: {standing_charge:.2f}p per day")
    except Exception as e:
        print(f"  ❌ Failed to get standing charge: {e}")
        return False
    
    # Test consumption data
    print("\n⚡ Testing Consumption Data:")
    try:
        start_date = f"{date.today()}T00:00:00Z"
        end_date = f"{date.today()}T23:59:59Z"
        consumption_data = ha_source.get_consumption_data(start_date, end_date)
        
        if consumption_data:
            total_consumption = sum(float(entry['consumptionDelta']) for entry in consumption_data)
            total_cost = sum(float(entry['costDeltaWithTax']) for entry in consumption_data)
            
            print(f"  ✅ Retrieved {len(consumption_data)} consumption periods")
            print(f"  ✅ Total consumption today: {total_consumption / 1000:.4f} kWh")
            print(f"  ✅ Total cost today: £{total_cost / 100:.2f}")
            
            # Show sample data
            if len(consumption_data) > 0:
                sample = consumption_data[0]
                print(f"  📊 Sample period:")
                print(f"     Time: {sample['readAt']}")
                print(f"     Consumption: {sample['consumptionDelta']} Wh")
                print(f"     Cost: {sample['costDeltaWithTax']:.2f}p")
        else:
            print("  ⚠️  No consumption data found for today")
            print("     This might be normal if it's early in the day")
            
    except Exception as e:
        print(f"  ❌ Failed to get consumption data: {e}")
        traceback.print_exc()
        return False
    
    print("\n🎉 Home Assistant integration test completed successfully!")
    return True


def test_data_source_factory():
    """Test the data source factory selection logic."""
    print("\n🏭 Testing Data Source Factory:")
    try:
        info = DataSourceFactory.get_data_source_info()
        print(f"  HA Configured: {'✅' if info['ha_configured'] else '❌'}")
        print(f"  HA Available: {'✅' if info['ha_available'] else '❌'}")
        print(f"  Octopus Available: {'✅' if info['octopus_available'] else '❌'}")
        print(f"  Selected Source: {info['selected_source']}")
        
        if info['selected_source'] == 'home_assistant':
            print("  ✅ Factory will use Home Assistant data source")
        elif info['selected_source'] == 'octopus':
            print("  ✅ Factory will use Octopus data source")
        else:
            print("  ❌ No valid data source available")
            return False
            
    except Exception as e:
        print(f"  ❌ Factory test failed: {e}")
        return False
    
    return True


def main():
    """Main test function."""
    print("🐙 Octopus MinMax Bot - Home Assistant Integration Test")
    print("=" * 60)
    
    # Test HA configuration
    ha_success = test_ha_configuration()
    
    # Test factory
    factory_success = test_data_source_factory()
    
    print("\n" + "=" * 60)
    if ha_success and factory_success:
        print("🎉 All tests passed! Your Home Assistant integration is ready.")
    else:
        print("❌ Some tests failed. Please check your configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()
