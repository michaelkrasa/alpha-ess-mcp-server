# Alpha ESS MCP Server

[![smithery badge](https://smithery.ai/badge/@michaelkrasa/alpha-ess-mcp-server)](https://smithery.ai/server/@michaelkrasa/alpha-ess-mcp-server)

A Model Context Protocol (MCP) server that provides access to Alpha ESS solar inverter and battery system data through the official Alpha ESS Open API.

## Installation

```bash
uv sync
```

## Configuration

Create a `.env` file in the project root:

```env
ALPHA_ESS_APP_ID=your_app_id_here
ALPHA_ESS_APP_SECRET=your_app_secret_here
```

To get your Alpha ESS API credentials:
1. Visit [https://open.alphaess.com/](https://open.alphaess.com/)
2. Create a developer account
3. Add your inverter system using the Serial Number (SN) and CheckCode
4. Obtain your AppID and AppSecret

## Usage with Claude Desktop

Add to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "alpha-ess": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/path/to/alpha-ess-mcp-server/main.py"
      ],
      "env": {
        "ALPHA_ESS_APP_ID": "your_app_id_here",
        "ALPHA_ESS_APP_SECRET": "your_app_secret_here"
      }
    }
  }
}
```

## Available Tools

### Authentication & System Management
- `authenticate_alphaess()` - Validate API credentials
- `get_ess_list()` - List all registered Alpha ESS systems

### Data Retrieval
- `get_alpha_ess_data()` - Get comprehensive energy statistics for all systems
- `get_last_power_data(serial?)` - Get real-time power data snapshot
- `get_one_day_power_data(query_date, serial?)` - Get detailed power data for a specific date
- `get_one_date_energy_data(query_date, serial?)` - Get energy summary for a specific date

### Battery Configuration
- `get_charge_config(serial?)` - Get current battery charging configuration
- `get_discharge_config(serial?)` - Get current battery discharge configuration
- `set_battery_charge(enabled, dp1_start, dp1_end, dp2_start, dp2_end, charge_cutoff_soc, serial?)` - Configure battery charging schedule
- `set_battery_discharge(enabled, dp1_start, dp1_end, dp2_start, dp2_end, discharge_cutoff_soc, serial?)` - Configure battery discharge schedule

### Parameters
- `serial` (optional) - System serial number. If not provided, automatically selects the first system if only one exists
- `query_date` - Date in YYYY-MM-DD format
- `enabled` - Boolean to enable/disable the configuration
- `dp1_start/dp1_end, dp2_start/dp2_end` - Time periods in HH:MM format (minutes must be :00, :15, :30, :45)
- `charge_cutoff_soc/discharge_cutoff_soc` - SOC percentage (0-100)

## Testing

```bash
uv run python test_methods.py
```

## License

MIT License

## References

- [Alpha ESS Open API Documentation](https://open.alphaess.com/developmentManagement/apiList)
- [alphaess-openAPI Library](https://github.com/CharlesGillanders/alphaess-openAPI)
- [Model Context Protocol](https://modelcontextprotocol.io/)
