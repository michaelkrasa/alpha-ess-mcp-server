# Alpha ESS MCP Server

A comprehensive MCP (Model Context Protocol) server that provides seamless access to Alpha ESS solar inverter and battery system data through the official Alpha ESS Open API. Built
with Python using FastMCP, this server enables AI assistants to monitor, analyze, and control Alpha ESS energy storage systems.

## Features

### 🔐 Authentication & Connection Management

- **Secure API authentication** with Alpha ESS Open API
- **Automatic connection management** with proper resource cleanup
- **Environment-based credential management**

### 📊 Data Retrieval & Monitoring

- **Real-time power data** - Live solar generation, battery status, grid usage
- **Historical energy data** - Daily, weekly, and custom date range statistics
- **System information** - List and manage multiple ESS systems
- **Structured data responses** - Enhanced formatting with summaries and metadata

### ⚙️ System Configuration

- **Battery charge scheduling** - Configure automated charging periods and limits
- **Battery discharge control** - Set discharge periods and SOC thresholds
- **Configuration validation** - Real-time validation of settings before application

### 🎯 Enhanced Data Processing

- **Intelligent data structuring** - Raw API data transformed into readable formats
- **Time series analysis** - Automatic calculation of energy statistics and trends
- **Multi-system support** - Handle multiple Alpha ESS installations
- **Comprehensive error handling** - Detailed error messages and fallback mechanisms

## Quick Start

### 1. Alpha ESS API Registration

Register with the Alpha ESS Open API to get your credentials:

1. Visit [https://open.alphaess.com/](https://open.alphaess.com/)
2. Create a free developer account
3. Add your inverter system using the Serial Number (SN) and CheckCode
4. Obtain your AppID and AppSecret from the developer portal

### 2. Installation

```bash
# Install dependencies using uv (recommended)
uv sync
```

### 3. Configuration

Create a `.env` file in the project root:

```env
ALPHA_ESS_APP_ID=your_app_id_here
ALPHA_ESS_APP_SECRET=your_app_secret_here
```

### 4. Testing

Test the server functionality before integration:

```bash
# Test authentication and basic functionality
uv run python test_methods.py
```

## Usage with Claude Desktop

Add the following configuration to your Claude Desktop config file:

### macOS

`~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows

`%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "alpha-ess": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/path/to/alpha-ess-mcp/main.py"
      ],
      "env": {
        "ALPHA_ESS_APP_ID": "your_app_id_here",
        "ALPHA_ESS_APP_SECRET": "your_app_secret_here"
      }
    }
  }
}
```

Alternatively, if using the `.env` file:

```json
{
  "mcpServers": {
    "alpha-ess": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/path/to/alpha-ess-mcp/main.py"
      ]
    }
  }
}
```

## Available Tools

### Core System Tools

#### `authenticate_alphaess()`

Validates your Alpha ESS API credentials.

**Returns:**

```json
{
  "success": true,
  "message": "Successfully authenticated with Alpha ESS API",
  "authenticated": true
}
```

#### `get_ess_list()`

Retrieves all Alpha ESS systems associated with your account.

**Returns:** List of systems with structured metadata including system details and serial numbers.

### Data Retrieval Tools

#### `get_alpha_ess_data()`

Gets comprehensive statistical energy data for analysis.

**Parameters:**

- `serial` (optional): System serial number (uses default if not provided)

**Returns:** Structured energy statistics with enhanced formatting and summary data.

#### `get_last_power_data(serial?)`

Retrieves real-time power data snapshot.

**Returns:** Current solar generation, battery status, grid usage, and load consumption with organized data structure.

#### `get_one_day_power_data(query_date, serial?)`

Gets detailed power data for a specific date.

**Parameters:**

- `query_date`: Date in YYYY-MM-DD format
- `serial` (optional): System serial number

**Returns:** Time-series power data with automatic analysis including:

- Peak solar generation
- Battery SOC trends
- Grid import/export totals
- Energy consumption statistics

#### `get_one_date_energy_data(query_date, serial?)`

Retrieves comprehensive energy data for a specific date.

**Parameters:**

- `query_date`: Date in YYYY-MM-DD format
- `serial` (optional): System serial number

**Returns:** Daily energy summary with structured insights.

### Configuration Management Tools

#### `get_charge_config(serial?)`

Retrieves current battery charging configuration.

**Returns:** Structured charging settings including:

- Enabled status and active periods
- Time schedules for dual charging windows
- SOC limits and thresholds

#### `get_discharge_config(serial?)`

Gets current battery discharge configuration.

**Returns:** Discharge settings with period details and SOC limits.

#### `set_battery_charge(enabled, dp1_start, dp1_end, dp2_start, dp2_end, charge_cutoff_soc, serial?)`

Configures battery charging schedule.

**Parameters:**

- `enabled`: Enable/disable charging control
- `dp1_start/dp1_end`: First charging period (HH:MM format)
- `dp2_start/dp2_end`: Second charging period (HH:MM format)
- `charge_cutoff_soc`: Maximum charging SOC percentage
- `serial` (optional): System serial number

#### `set_battery_discharge(enabled, dp1_start, dp1_end, dp2_start, dp2_end, discharge_cutoff_soc, serial?)`

Configures battery discharge schedule.

**Parameters:** Similar to charging configuration but for discharge periods and minimum SOC limits.

## Data Structure & Response Format

All tools return standardized responses with the following structure:

```json
{
  "success": true,
  "message": "Human-readable description",
  "data_type": "timeseries|config|snapshot|summary|system_list",
  "metadata": {
    "timestamp": "ISO timestamp",
    "serial_used": "system_serial_number",
    "additional_context": "..."
  },
  "data": "raw_api_response",
  "structured": "enhanced_formatted_data"
}
```

### Enhanced Data Features

- **Time Series Analysis**: Automatic calculation of energy statistics, peak values, and trends
- **Smart Field Mapping**: API field names converted to readable formats (e.g., `ppv` → `solar_power`)
- **Unit Standardization**: Consistent units with clear labeling (W, kWh, %)
- **Summary Statistics**: Automatic generation of daily/period summaries

### Testing

```bash
# Test individual functions
uv run python test_methods.py

# Run the MCP server
uv run python main.py
```

### Adding New Features

The server is built on [FastMCP](https://github.com/jlowin/fastmcp) and uses the [alphaess-openAPI](https://github.com/CharlesGillanders/alphaess-openAPI) library. To add new
functionality:

1. Add the tool function with `@mcp.tool()` decorator
2. Implement proper error handling and response formatting
3. Use the `create_enhanced_response()` helper for consistent output
4. Test with `test_methods.py` before integration

## License

MIT License - Same as the underlying alphaess-openAPI library.

## References

- [Alpha ESS Open API Documentation](https://open.alphaess.com/developmentManagement/apiList)
- [alphaess-openAPI Library](https://github.com/CharlesGillanders/alphaess-openAPI)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
