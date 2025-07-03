import os
from datetime import datetime
from typing import Any, Optional, Literal, Dict, List

from alphaess.alphaess import alphaess
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("alpha-ess-mcp")

# Data type definitions for better structure
DataType = Literal["timeseries", "config", "snapshot", "summary", "system_list"]


def create_enhanced_response(
        success: bool,
        message: str,
        raw_data: Any,
        data_type: DataType,
        serial_used: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        structured_data: Optional[Any] = None
) -> Dict[str, Any]:
    """Create a standardized response with enhanced structure"""
    response = {
        "success": success,
        "message": message,
        "data_type": data_type,
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            **({"serial_used": serial_used} if serial_used else {}),
            **(metadata or {})
        },
        "data": raw_data
    }

    if structured_data is not None:
        response["structured"] = structured_data

    return response


def structure_timeseries_data(raw_data: List[Dict], serial: str) -> Dict[str, Any]:
    """Convert inefficient timeseries to structured format"""
    if not raw_data:
        return {"series": [], "summary": {}}

    # Extract time series data (remove redundant serial)
    series = []
    for record in raw_data:
        # Convert timestamp and remove redundant fields
        timestamp = record.get('uploadTime', '')
        series.append({
            "timestamp": timestamp,
            "solar_power": record.get('ppv', 0),  # W
            "load_power": record.get('load', 0),  # W  
            "battery_soc": record.get('cbat', 0),  # %
            "grid_feedin": record.get('feedIn', 0),  # W
            "grid_import": record.get('gridCharge', 0),  # W
            "ev_charging": record.get('pchargingPile', 0)  # W
        })

    # Calculate summary statistics
    solar_values = [r['solar_power'] for r in series]
    load_values = [r['load_power'] for r in series]
    battery_values = [r['battery_soc'] for r in series]
    feedin_values = [r['grid_feedin'] for r in series]

    summary = {
        "total_records": len(series),
        "interval_minutes": 10,
        "time_span_hours": len(series) * 10 / 60,
        "solar": {
            "peak_power": max(solar_values) if solar_values else 0,
            "avg_power": sum(solar_values) / len(solar_values) if solar_values else 0,
            "total_generation_kwh": sum(solar_values) * 10 / 60 / 1000  # Convert W*10min to kWh
        },
        "battery": {
            "max_soc": max(battery_values) if battery_values else 0,
            "min_soc": min(battery_values) if battery_values else 0,
            "avg_soc": sum(battery_values) / len(battery_values) if battery_values else 0
        },
        "grid": {
            "total_feedin_kwh": sum(feedin_values) * 10 / 60 / 1000,
            "peak_feedin": max(feedin_values) if feedin_values else 0
        },
        "load": {
            "peak_power": max(load_values) if load_values else 0,
            "avg_power": sum(load_values) / len(load_values) if load_values else 0,
            "total_consumption_kwh": sum(load_values) * 10 / 60 / 1000
        }
    }

    return {
        "series": series,
        "summary": summary
    }


def structure_config_data(raw_data: Dict[str, Any], config_type: str) -> Dict[str, Any]:
    """Structure configuration data with better field names"""
    if config_type == "charge":
        return {
            "enabled": bool(raw_data.get('gridCharge', 0)),
            "periods": [
                {
                    "period": 1,
                    "start_time": raw_data.get('timeChaf1', '00:00'),
                    "end_time": raw_data.get('timeChae1', '00:00'),
                    "active": raw_data.get('timeChaf1', '00:00') != '00:00' or raw_data.get('timeChae1', '00:00') != '00:00'
                },
                {
                    "period": 2,
                    "start_time": raw_data.get('timeChaf2', '00:00'),
                    "end_time": raw_data.get('timeChae2', '00:00'),
                    "active": raw_data.get('timeChaf2', '00:00') != '00:00' or raw_data.get('timeChae2', '00:00') != '00:00'
                }
            ],
            "charge_limit_soc": raw_data.get('batHighCap', 100),
            "units": {"soc": "%", "time": "HH:MM"}
        }
    elif config_type == "discharge":
        return {
            "enabled": bool(raw_data.get('ctrDis', 0)),
            "periods": [
                {
                    "period": 1,
                    "start_time": raw_data.get('timeDisf1', '00:00'),
                    "end_time": raw_data.get('timeDise1', '00:00'),
                    "active": raw_data.get('timeDisf1', '00:00') != '00:00' or raw_data.get('timeDise1', '00:00') != '00:00'
                },
                {
                    "period": 2,
                    "start_time": raw_data.get('timeDisf2', '00:00'),
                    "end_time": raw_data.get('timeDise2', '00:00'),
                    "active": raw_data.get('timeDisf2', '00:00') != '00:00' or raw_data.get('timeDise2', '00:00') != '00:00'
                }
            ],
            "discharge_limit_soc": raw_data.get('batUseCap', 10),
            "units": {"soc": "%", "time": "HH:MM"}
        }
    return raw_data


def structure_snapshot_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Structure real-time snapshot data with clear field names"""
    return {
        "solar": {
            "total_power": raw_data.get('ppv', 0),
            "panels": {
                "panel_1": raw_data.get('ppvDetail', {}).get('ppv1', 0),
                "panel_2": raw_data.get('ppvDetail', {}).get('ppv2', 0),
                "panel_3": raw_data.get('ppvDetail', {}).get('ppv3', 0),
                "panel_4": raw_data.get('ppvDetail', {}).get('ppv4', 0)
            }
        },
        "battery": {
            "state_of_charge": raw_data.get('soc', 0),
            "power": raw_data.get('pbat', 0)  # Positive = charging, Negative = discharging
        },
        "grid": {
            "total_power": raw_data.get('pgrid', 0),  # Positive = importing, Negative = exporting
            "phases": {
                "l1_power": raw_data.get('pgridDetail', {}).get('pmeterL1', 0),
                "l2_power": raw_data.get('pgridDetail', {}).get('pmeterL2', 0),
                "l3_power": raw_data.get('pgridDetail', {}).get('pmeterL3', 0)
            }
        },
        "load": {
            "total_power": raw_data.get('pload', 0),
            "phases": {
                "l1_real": raw_data.get('prealL1', 0),
                "l2_real": raw_data.get('prealL2', 0),
                "l3_real": raw_data.get('prealL3', 0)
            }
        },
        "ev_charging": {
            "total_power": raw_data.get('pev', 0),
            "stations": {
                "ev1": raw_data.get('pevDetail', {}).get('ev1Power', 0),
                "ev2": raw_data.get('pevDetail', {}).get('ev2Power', 0),
                "ev3": raw_data.get('pevDetail', {}).get('ev3Power', 0),
                "ev4": raw_data.get('pevDetail', {}).get('ev4Power', 0)
            }
        },
        "units": {
            "power": "W",
            "soc": "%"
        }
    }


def get_alpha_credentials():
    """Get Alpha ESS credentials from environment variables"""
    app_id = os.getenv('ALPHA_ESS_APP_ID')
    app_secret = os.getenv('ALPHA_ESS_APP_SECRET')

    if not app_id or not app_secret:
        raise ValueError("ALPHA_ESS_APP_ID and ALPHA_ESS_APP_SECRET environment variables must be set")

    return app_id, app_secret


async def get_default_serial() -> dict[str, Any]:
    """
    Get the default serial number to use. If only one system is registered,
    returns that serial. If multiple systems, returns list for user to choose.
    
    Returns:
        dict: Result with serial info
    """
    client = None
    try:
        app_id, app_secret = get_alpha_credentials()
        client = alphaess(app_id, app_secret)

        # Get ESS list
        ess_list = await client.getESSList()

        if not ess_list or len(ess_list) == 0:
            return {
                "success": False,
                "message": "No Alpha ESS systems found in your account",
                "serial": None,
                "systems": []
            }

        if len(ess_list) == 1:
            # Auto-select the only system
            system = ess_list[0]
            serial = system.get('sysSn') if isinstance(system, dict) else getattr(system, 'sysSn', None)
            return {
                "success": True,
                "message": f"Auto-selected single system: {serial}",
                "serial": serial,
                "systems": ess_list
            }
        else:
            # Multiple systems - return list for user choice
            systems_info = []
            for system in ess_list:
                if isinstance(system, dict):
                    systems_info.append({
                        "serial": system.get('sysSn'),
                        "name": system.get('sysName', 'Unknown'),
                        "status": system.get('sysStatus', 'Unknown')
                    })
                else:
                    systems_info.append({
                        "serial": getattr(system, 'sysSn', 'Unknown'),
                        "name": getattr(system, 'sysName', 'Unknown'),
                        "status": getattr(system, 'sysStatus', 'Unknown')
                    })

            return {
                "success": True,
                "message": f"Found {len(ess_list)} systems. Please specify which serial to use.",
                "serial": None,
                "systems": systems_info
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting system list: {str(e)}",
            "serial": None,
            "systems": []
        }
    finally:
        if client:
            await client.close()


@mcp.tool()
async def authenticate_alphaess() -> dict[str, Any]:
    """
    Authenticate with the Alpha ESS Open API to validate credentials.
    
    Returns:
        dict: Authentication result with success status and message
    """
    client = None
    try:
        app_id, app_secret = get_alpha_credentials()

        # Create Alpha ESS client instance with credentials
        client = alphaess(app_id, app_secret)

        # Attempt authentication
        auth_result = await client.authenticate()

        if auth_result:
            return {
                "success": True,
                "message": "Successfully authenticated with Alpha ESS API",
                "authenticated": True
            }
        else:
            return {
                "success": False,
                "message": "Authentication failed - invalid credentials or API error",
                "authenticated": False
            }

    except ValueError as e:
        return {
            "success": False,
            "message": f"Configuration error: {str(e)}",
            "authenticated": False
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error during authentication: {str(e)}",
            "authenticated": False
        }
    finally:
        # Clean up the client connection
        if client:
            await client.close()


@mcp.tool()
async def get_alpha_ess_data() -> dict[str, Any]:
    """
    Get statistical energy data for all registered Alpha ESS systems.
    
    Returns:
        dict: Energy data with success status and system information
    """
    client = None
    try:
        app_id, app_secret = get_alpha_credentials()
        client = alphaess(app_id, app_secret)

        # Get energy data
        data = await client.getdata()

        if data is not None:
            return {
                "success": True,
                "message": "Successfully retrieved Alpha ESS energy data",
                "data": data
            }
        else:
            return {
                "success": False,
                "message": "Failed to retrieve energy data - API returned None",
                "data": None
            }

    except ValueError as e:
        return {
            "success": False,
            "message": f"Configuration error: {str(e)}",
            "data": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error retrieving energy data: {str(e)}",
            "data": None
        }
    finally:
        if client:
            await client.close()


@mcp.tool()
async def get_ess_list() -> dict[str, Any]:
    """
    Get list of registered Alpha ESS systems with auto-selection logic.
    Returns enhanced system information with structured metadata.
    
    Returns:
        dict: Enhanced response with system list and auto-selection recommendations
    """
    serial_info = await get_default_serial()

    if serial_info['success']:
        return create_enhanced_response(
            success=True,
            message=serial_info['message'],
            raw_data=serial_info['systems'],
            data_type="system_list",
            metadata={
                "total_systems": len(serial_info['systems']),
                "auto_selected_serial": serial_info.get('serial'),
                "selection_strategy": "single_system_auto" if serial_info.get('serial') else "multiple_systems_manual"
            },
            structured_data={
                "recommended_serial": serial_info.get('serial'),
                "systems": serial_info['systems'],
                "requires_selection": serial_info.get('serial') is None
            }
        )
    else:
        return create_enhanced_response(
            success=False,
            message=serial_info['message'],
            raw_data=None,
            data_type="system_list",
            metadata={"error_type": "no_systems_found"}
        )


@mcp.tool()
async def get_last_power_data(serial: Optional[str] = None) -> dict[str, Any]:
    """
    Get the latest real-time power data for a specific Alpha ESS system.
    Returns structured snapshot with clear field names and units.
    If no serial provided, auto-selects if only one system exists.
    
    Args:
        serial: The serial number of the Alpha ESS system (optional)
        
    Returns:
        dict: Enhanced response with structured real-time power data
    """
    client = None
    try:
        # Auto-discover serial if not provided
        if not serial:
            serial_info = await get_default_serial()
            if not serial_info['success'] or not serial_info['serial']:
                return create_enhanced_response(
                    success=False,
                    message=f"Serial auto-discovery failed: {serial_info['message']}",
                    raw_data=None,
                    data_type="snapshot",
                    metadata={"available_systems": serial_info.get('systems', [])}
                )
            serial = serial_info['serial']

        app_id, app_secret = get_alpha_credentials()
        client = alphaess(app_id, app_secret)

        # Get last power data
        power_data = await client.getLastPowerData(serial)

        # Structure the snapshot data
        structured = structure_snapshot_data(power_data)

        return create_enhanced_response(
            success=True,
            message=f"Successfully retrieved last power data for {serial}",
            raw_data=power_data,
            data_type="snapshot",
            serial_used=serial,
            metadata={
                "snapshot_type": "real_time_power",
                "units": {"power": "W", "soc": "%"}
            },
            structured_data=structured
        )

    except ValueError as e:
        return create_enhanced_response(
            success=False,
            message=f"Configuration error: {str(e)}",
            raw_data=None,
            data_type="snapshot"
        )
    except Exception as e:
        return create_enhanced_response(
            success=False,
            message=f"Error retrieving power data: {str(e)}",
            raw_data=None,
            data_type="snapshot"
        )
    finally:
        if client:
            await client.close()


@mcp.tool()
async def get_one_day_power_data(query_date: str, serial: Optional[str] = None) -> dict[str, Any]:
    """
    Get one day's power data for a specific Alpha ESS system.
    Returns structured timeseries data with 10-minute intervals and summary statistics.
    If no serial provided, auto-selects if only one system exists.
    
    Args:
        query_date: Date in YYYY-MM-DD format
        serial: The serial number of the Alpha ESS system (optional)
        
    Returns:
        dict: Enhanced response with structured timeseries data and analytics
    """
    client = None
    try:
        # Auto-discover serial if not provided
        if not serial:
            serial_info = await get_default_serial()
            if not serial_info['success'] or not serial_info['serial']:
                return create_enhanced_response(
                    success=False,
                    message=f"Serial auto-discovery failed: {serial_info['message']}",
                    raw_data=None,
                    data_type="timeseries",
                    metadata={"available_systems": serial_info.get('systems', [])}
                )
            serial = serial_info['serial']

        app_id, app_secret = get_alpha_credentials()
        client = alphaess(app_id, app_secret)

        # Get one day power data
        power_data = await client.getOneDayPowerBySn(serial, query_date)

        # Structure the timeseries data
        structured = structure_timeseries_data(power_data, serial)

        return create_enhanced_response(
            success=True,
            message=f"Successfully retrieved power data for {serial} on {query_date}",
            raw_data=power_data,
            data_type="timeseries",
            serial_used=serial,
            metadata={
                "query_date": query_date,
                "interval_minutes": 10,
                "total_records": len(power_data) if power_data else 0,
                "units": {"power": "W", "soc": "%", "energy": "kWh"}
            },
            structured_data=structured
        )

    except ValueError as e:
        return create_enhanced_response(
            success=False,
            message=f"Configuration or parameter error: {str(e)}",
            raw_data=None,
            data_type="timeseries"
        )
    except Exception as e:
        return create_enhanced_response(
            success=False,
            message=f"Error retrieving one day power data: {str(e)}",
            raw_data=None,
            data_type="timeseries"
        )
    finally:
        if client:
            await client.close()


@mcp.tool()
async def get_one_date_energy_data(query_date: str, serial: Optional[str] = None) -> dict[str, Any]:
    """
    Get energy data for a specific date and Alpha ESS system.
    If no serial provided, auto-selects if only one system exists.
    
    Args:
        query_date: Date in YYYY-MM-DD format
        serial: The serial number of the Alpha ESS system (optional)
        
    Returns:
        dict: Energy data for the specified date with success status
    """
    client = None
    try:
        # Auto-discover serial if not provided
        if not serial:
            serial_info = await get_default_serial()
            if not serial_info['success'] or not serial_info['serial']:
                return {
                    "success": False,
                    "message": f"Serial auto-discovery failed: {serial_info['message']}",
                    "data": None,
                    "available_systems": serial_info.get('systems', [])
                }
            serial = serial_info['serial']

        app_id, app_secret = get_alpha_credentials()
        client = alphaess(app_id, app_secret)

        # Get one date energy data
        energy_data = await client.getOneDateEnergyBySn(serial, query_date)

        return {
            "success": True,
            "message": f"Successfully retrieved energy data for {serial} on {query_date}",
            "data": energy_data,
            "serial_used": serial
        }

    except ValueError as e:
        return {
            "success": False,
            "message": f"Configuration or parameter error: {str(e)}",
            "data": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error retrieving energy data: {str(e)}",
            "data": None
        }
    finally:
        if client:
            await client.close()


@mcp.tool()
async def get_charge_config(serial: Optional[str] = None) -> dict[str, Any]:
    """
    Get battery charging configuration for a specific Alpha ESS system.
    Returns structured configuration with clear period definitions and status.
    If no serial provided, auto-selects if only one system exists.
    
    Args:
        serial: The serial number of the Alpha ESS system (optional)
        
    Returns:
        dict: Enhanced response with structured charging configuration
    """
    client = None
    try:
        # Auto-discover serial if not provided
        if not serial:
            serial_info = await get_default_serial()
            if not serial_info['success'] or not serial_info['serial']:
                return create_enhanced_response(
                    success=False,
                    message=f"Serial auto-discovery failed: {serial_info['message']}",
                    raw_data=None,
                    data_type="config",
                    metadata={"available_systems": serial_info.get('systems', [])}
                )
            serial = serial_info['serial']

        app_id, app_secret = get_alpha_credentials()
        client = alphaess(app_id, app_secret)

        # Get charge config
        config = await client.getChargeConfigInfo(serial)

        # Structure the config data
        structured = structure_config_data(config, "charge")

        return create_enhanced_response(
            success=True,
            message=f"Successfully retrieved charge config for {serial}",
            raw_data=config,
            data_type="config",
            serial_used=serial,
            metadata={
                "config_type": "battery_charging",
                "total_periods": 2,
                "units": {"soc": "%", "time": "HH:MM"}
            },
            structured_data=structured
        )

    except ValueError as e:
        return create_enhanced_response(
            success=False,
            message=f"Configuration error: {str(e)}",
            raw_data=None,
            data_type="config"
        )
    except Exception as e:
        return create_enhanced_response(
            success=False,
            message=f"Error retrieving charge config: {str(e)}",
            raw_data=None,
            data_type="config"
        )
    finally:
        if client:
            await client.close()


@mcp.tool()
async def get_discharge_config(serial: Optional[str] = None) -> dict[str, Any]:
    """
    Get battery discharge configuration for a specific Alpha ESS system.
    Returns structured configuration with clear period definitions and status.
    If no serial provided, auto-selects if only one system exists.
    
    Args:
        serial: The serial number of the Alpha ESS system (optional)
        
    Returns:
        dict: Enhanced response with structured discharge configuration
    """
    client = None
    try:
        # Auto-discover serial if not provided
        if not serial:
            serial_info = await get_default_serial()
            if not serial_info['success'] or not serial_info['serial']:
                return create_enhanced_response(
                    success=False,
                    message=f"Serial auto-discovery failed: {serial_info['message']}",
                    raw_data=None,
                    data_type="config",
                    metadata={"available_systems": serial_info.get('systems', [])}
                )
            serial = serial_info['serial']

        app_id, app_secret = get_alpha_credentials()
        client = alphaess(app_id, app_secret)

        # Get discharge config
        config = await client.getDisChargeConfigInfo(serial)

        # Structure the config data
        structured = structure_config_data(config, "discharge")

        return create_enhanced_response(
            success=True,
            message=f"Successfully retrieved discharge config for {serial}",
            raw_data=config,
            data_type="config",
            serial_used=serial,
            metadata={
                "config_type": "battery_discharging",
                "total_periods": 2,
                "units": {"soc": "%", "time": "HH:MM"}
            },
            structured_data=structured
        )

    except ValueError as e:
        return create_enhanced_response(
            success=False,
            message=f"Configuration error: {str(e)}",
            raw_data=None,
            data_type="config"
        )
    except Exception as e:
        return create_enhanced_response(
            success=False,
            message=f"Error retrieving discharge config: {str(e)}",
            raw_data=None,
            data_type="config"
        )
    finally:
        if client:
            await client.close()


@mcp.tool()
async def set_battery_charge(
        enabled: bool,
        dp1_start: str,
        dp1_end: str,
        dp2_start: str,
        dp2_end: str,
        charge_cutoff_soc: float,
        serial: Optional[str] = None
) -> dict[str, Any]:
    """
    Set battery charging configuration for a specific Alpha ESS system.
    If no serial provided, auto-selects if only one system exists.
    
    Args:
        enabled: True to enable charging from grid, False to disable
        dp1_start: Start time for charging period 1 (HH:MM format, minutes must be :00, :15, :30, :45)
        dp1_end: End time for charging period 1 (HH:MM format, minutes must be :00, :15, :30, :45)
        dp2_start: Start time for charging period 2 (HH:MM format, minutes must be :00, :15, :30, :45)
        dp2_end: End time for charging period 2 (HH:MM format, minutes must be :00, :15, :30, :45)
        charge_cutoff_soc: Percentage to stop charging from grid at (0-100)
        serial: The serial number of the Alpha ESS system (optional)
        
    Returns:
        dict: Result of charge configuration update with success status
    """
    client = None
    try:
        # Auto-discover serial if not provided
        if not serial:
            serial_info = await get_default_serial()
            if not serial_info['success'] or not serial_info['serial']:
                return {
                    "success": False,
                    "message": f"Serial auto-discovery failed: {serial_info['message']}",
                    "data": None,
                    "available_systems": serial_info.get('systems', [])
                }
            serial = serial_info['serial']

        app_id, app_secret = get_alpha_credentials()
        client = alphaess(app_id, app_secret)

        # Set battery charge configuration
        result = await client.updateChargeConfigInfo(
            serial, enabled, dp1_start, dp1_end,
            dp2_start, dp2_end, charge_cutoff_soc
        )

        return {
            "success": True,
            "message": f"Successfully updated charge config for {serial}",
            "data": result,
            "serial_used": serial
        }

    except ValueError as e:
        return {
            "success": False,
            "message": f"Configuration or parameter error: {str(e)}",
            "data": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error setting battery charge config: {str(e)}",
            "data": None
        }
    finally:
        if client:
            await client.close()


@mcp.tool()
async def set_battery_discharge(
        enabled: bool,
        dp1_start: str,
        dp1_end: str,
        dp2_start: str,
        dp2_end: str,
        discharge_cutoff_soc: float,
        serial: Optional[str] = None
) -> dict[str, Any]:
    """
    Set battery discharge configuration for a specific Alpha ESS system.
    If no serial provided, auto-selects if only one system exists.
    
    Args:
        enabled: True to enable battery discharge, False to disable
        dp1_start: Start time for discharge period 1 (HH:MM format, minutes must be :00, :15, :30, :45)
        dp1_end: End time for discharge period 1 (HH:MM format, minutes must be :00, :15, :30, :45)
        dp2_start: Start time for discharge period 2 (HH:MM format, minutes must be :00, :15, :30, :45)
        dp2_end: End time for discharge period 2 (HH:MM format, minutes must be :00, :15, :30, :45)
        discharge_cutoff_soc: Percentage to stop discharging battery at (0-100)
        serial: The serial number of the Alpha ESS system (optional)
        
    Returns:
        dict: Result of discharge configuration update with success status
    """
    client = None
    try:
        # Auto-discover serial if not provided
        if not serial:
            serial_info = await get_default_serial()
            if not serial_info['success'] or not serial_info['serial']:
                return {
                    "success": False,
                    "message": f"Serial auto-discovery failed: {serial_info['message']}",
                    "data": None,
                    "available_systems": serial_info.get('systems', [])
                }
            serial = serial_info['serial']

        app_id, app_secret = get_alpha_credentials()
        client = alphaess(app_id, app_secret)

        # Update the discharge configuration using the proper method signature
        result = await client.updateDisChargeConfigInfo(
            serial,
            discharge_cutoff_soc,  # batUseCap
            1 if enabled else 0,  # ctrDis
            dp1_end,
            dp2_end,
            dp1_start,
            dp2_start
        )

        return {
            "success": True,
            "message": f"Successfully updated discharge config for {serial}",
            "data": result,
            "serial_used": serial
        }

    except ValueError as e:
        return {
            "success": False,
            "message": f"Configuration or parameter error: {str(e)}",
            "data": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error setting battery discharge config: {str(e)}",
            "data": None
        }
    finally:
        if client:
            await client.close()


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run()
