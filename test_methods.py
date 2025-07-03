#!/usr/bin/env python3
"""
Alpha ESS MCP Server - Comprehensive Test Suite
Tests all MCP tool methods with real API calls.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from main import (
    authenticate_alphaess,
    get_alpha_ess_data,
    get_ess_list,
    get_last_power_data,
    get_one_day_power_data,
    get_one_date_energy_data,
    get_charge_config,
    get_discharge_config,
    set_battery_charge,
    set_battery_discharge
)

load_dotenv()


class AlphaESSTestSuite:
    """Comprehensive test suite for all Alpha ESS MCP Server methods"""
    
    def __init__(self):
        self.serial = None
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def check_credentials(self):
        """Check if credentials are available"""
        app_id = os.getenv('ALPHA_ESS_APP_ID')
        app_secret = os.getenv('ALPHA_ESS_APP_SECRET')
        
        if not app_id or not app_secret:
            print("ERROR: Missing Alpha ESS credentials in .env file")
            return False
        return True
    
    def log_result(self, test_name, success, message=""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            print(f"PASS: {test_name}")
        else:
            print(f"FAIL: {test_name} - {message}")
        
        if message and success:
            print(f"  {message}")
    
    async def test_authenticate(self):
        """Test authentication method"""
        try:
            result = await authenticate_alphaess()
            success = result['success']
            message = "Authentication successful" if success else result['message']
            self.log_result("authenticate_alphaess", success, message)
            return success
        except Exception as e:
            self.log_result("authenticate_alphaess", False, f"Exception: {str(e)}")
            return False
    
    async def test_get_alpha_ess_data(self):
        """Test get_alpha_ess_data method"""
        try:
            result = await get_alpha_ess_data()
            success = result['success']
            message = "Statistical data retrieved" if success else result['message']
            self.log_result("get_alpha_ess_data", success, message)
            return success
        except Exception as e:
            self.log_result("get_alpha_ess_data", False, f"Exception: {str(e)}")
            return False
    
    async def test_get_ess_list(self):
        """Test get_ess_list method and extract serial for other tests"""
        try:
            result = await get_ess_list()
            success = result['success']
            
            if success:
                structured = result.get('structured', {})
                systems = structured.get('systems', [])
                recommended_serial = structured.get('recommended_serial')
                
                # Store serial for other tests
                if recommended_serial:
                    self.serial = recommended_serial
                elif systems:
                    self.serial = systems[0].get('serial')
                
                message = f"Found {len(systems)} systems, using serial: {self.serial}"
                self.log_result("get_ess_list", success, message)
            else:
                self.log_result("get_ess_list", success, result['message'])
            
            return success
        except Exception as e:
            self.log_result("get_ess_list", False, f"Exception: {str(e)}")
            return False
    
    async def test_get_last_power_data(self):
        """Test get_last_power_data method"""
        try:
            result = await get_last_power_data(self.serial)
            success = result['success']
            
            if success:
                structured = result.get('structured', {})
                solar = structured.get('solar', {}).get('total_power', 0)
                battery = structured.get('battery', {}).get('state_of_charge', 0)
                message = f"Solar: {solar}W, Battery: {battery}%"
            else:
                message = result['message']
            
            self.log_result("get_last_power_data", success, message)
            return success
        except Exception as e:
            self.log_result("get_last_power_data", False, f"Exception: {str(e)}")
            return False
    
    async def test_get_one_day_power_data(self):
        """Test get_one_day_power_data method"""
        try:
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            result = await get_one_day_power_data(yesterday, self.serial)
            success = result['success']
            
            if success:
                structured = result.get('structured', {})
                series = structured.get('series', [])
                summary = structured.get('summary', {})
                solar_kwh = summary.get('solar', {}).get('total_generation_kwh', 0)
                message = f"Retrieved {len(series)} data points, {solar_kwh:.2f} kWh solar"
            else:
                message = result['message']
            
            self.log_result("get_one_day_power_data", success, message)
            return success
        except Exception as e:
            self.log_result("get_one_day_power_data", False, f"Exception: {str(e)}")
            return False
    
    async def test_get_one_date_energy_data(self):
        """Test get_one_date_energy_data method"""
        try:
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            result = await get_one_date_energy_data(yesterday, self.serial)
            success = result['success']
            message = f"Energy data for {yesterday}" if success else result['message']
            self.log_result("get_one_date_energy_data", success, message)
            return success
        except Exception as e:
            self.log_result("get_one_date_energy_data", False, f"Exception: {str(e)}")
            return False
    
    async def test_get_charge_config(self):
        """Test get_charge_config method"""
        try:
            result = await get_charge_config(self.serial)
            success = result['success']
            
            if success:
                structured = result.get('structured', {})
                enabled = structured.get('enabled', False)
                limit = structured.get('charge_limit_soc', 0)
                message = f"Enabled: {enabled}, Limit: {limit}%"
            else:
                message = result['message']
            
            self.log_result("get_charge_config", success, message)
            return success
        except Exception as e:
            self.log_result("get_charge_config", False, f"Exception: {str(e)}")
            return False
    
    async def test_get_discharge_config(self):
        """Test get_discharge_config method"""
        try:
            result = await get_discharge_config(self.serial)
            success = result['success']
            
            if success:
                structured = result.get('structured', {})
                enabled = structured.get('enabled', False)
                limit = structured.get('discharge_limit_soc', 0)
                message = f"Enabled: {enabled}, Limit: {limit}%"
            else:
                message = result['message']
            
            self.log_result("get_discharge_config", success, message)
            return success
        except Exception as e:
            self.log_result("get_discharge_config", False, f"Exception: {str(e)}")
            return False
    
    async def test_set_battery_charge(self):
        """Test set_battery_charge method (non-disruptive)"""
        try:
            # Get current config first
            current_config = await get_charge_config(self.serial)
            if not current_config['success']:
                self.log_result("set_battery_charge", False, "Cannot get current config")
                return False
            
            # Extract current settings
            structured = current_config.get('structured', {})
            enabled = structured.get('enabled', False)
            limit = structured.get('charge_limit_soc', 100)
            periods = structured.get('periods', [])
            
            period1 = periods[0] if len(periods) > 0 else {'start_time': '00:00', 'end_time': '00:00'}
            period2 = periods[1] if len(periods) > 1 else {'start_time': '00:00', 'end_time': '00:00'}
            
            # Set same configuration (no actual change)
            result = await set_battery_charge(
                enabled=enabled,
                dp1_start=period1['start_time'],
                dp1_end=period1['end_time'],
                dp2_start=period2['start_time'],
                dp2_end=period2['end_time'],
                charge_cutoff_soc=limit,
                serial=self.serial
            )
            
            success = result['success']
            message = f"Set charge config (no change)" if success else result['message']
            self.log_result("set_battery_charge", success, message)
            return success
        except Exception as e:
            self.log_result("set_battery_charge", False, f"Exception: {str(e)}")
            return False
    
    async def test_set_battery_discharge(self):
        """Test set_battery_discharge method (non-disruptive)"""
        try:
            # Get current config first
            current_config = await get_discharge_config(self.serial)
            if not current_config['success']:
                self.log_result("set_battery_discharge", False, "Cannot get current config")
                return False
            
            # Extract current settings
            structured = current_config.get('structured', {})
            enabled = structured.get('enabled', False)
            limit = structured.get('discharge_limit_soc', 10)
            periods = structured.get('periods', [])
            
            period1 = periods[0] if len(periods) > 0 else {'start_time': '00:00', 'end_time': '00:00'}
            period2 = periods[1] if len(periods) > 1 else {'start_time': '00:00', 'end_time': '00:00'}
            
            # Set same configuration (no actual change)
            result = await set_battery_discharge(
                enabled=enabled,
                dp1_start=period1['start_time'],
                dp1_end=period1['end_time'],
                dp2_start=period2['start_time'],
                dp2_end=period2['end_time'],
                discharge_cutoff_soc=limit,
                serial=self.serial
            )
            
            success = result['success']
            message = f"Set discharge config (no change)" if success else result['message']
            self.log_result("set_battery_discharge", success, message)
            return success
        except Exception as e:
            self.log_result("set_battery_discharge", False, f"Exception: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all tests in sequence"""
        print("Alpha ESS MCP Server - Comprehensive Test Suite")
        print("=" * 50)
        
        if not self.check_credentials():
            return False
        
        # Test authentication first
        if not await self.test_authenticate():
            print("Authentication failed - stopping tests")
            return False
        
        # Get system list and serial
        if not await self.test_get_ess_list():
            print("Cannot get system list - stopping tests")
            return False
        
        # Test all other methods
        await self.test_get_alpha_ess_data()
        await self.test_get_last_power_data()
        await self.test_get_one_day_power_data()
        await self.test_get_one_date_energy_data()
        await self.test_get_charge_config()
        await self.test_get_discharge_config()
        await self.test_set_battery_charge()
        await self.test_set_battery_discharge()
        
        # Print summary
        print("=" * 50)
        print(f"Tests completed: {self.passed_tests}/{self.total_tests}")
        print(f"Success rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("ALL TESTS PASSED")
            return True
        else:
            print(f"{self.total_tests - self.passed_tests} tests failed")
            return False


async def main():
    """Run the comprehensive test suite"""
    test_suite = AlphaESSTestSuite()
    success = await test_suite.run_all_tests()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
