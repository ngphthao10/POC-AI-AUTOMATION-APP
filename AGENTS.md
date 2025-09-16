# AGENTS.md

## Project Overview

AI Automation Python Application for VIB Bank's CSP (Customer Service Portal) administrative tasks. This is a console-based application that automates user role and branch management tasks using Amazon Nova Act AI browser automation.

**Key Features:**
- CSP Admin role and branch assignment automation
- Single worker mode for stability and reliability  
- Console-based interface with interactive menus
- PyInstaller-built executables for easy deployment
- JSON-based configuration system

## Setup Commands

### Development Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python console_app.py
```

### Build Commands
```bash
# macOS/Linux
chmod +x build.sh
./build.sh

# Windows  
build.bat

# Manual build
pyinstaller --onefile --name="ai_automation_app" console_app.py
```

### Testing Commands
```bash
# Run the CSP automation module directly
python -m src.csp.csp_admin_change_role_and_branch --input_file src/csp/input.json

# Test Nova Act configuration
python -c "from src.config.nova_act_config import get_nova_act_api_key; print('API Key configured')"
```

## Project Structure

```
ai_automation_python_app/
├── console_app.py              # Main console application
├── requirements.txt            # Python dependencies
├── build.sh / build.bat        # Build scripts
├── ai_automation_app.spec      # PyInstaller spec file
├── src/
│   ├── config/
│   │   └── nova_act_config.py  # Nova Act API key configuration
│   ├── csp/
│   │   ├── csp_admin_change_role_and_branch.py  # Main automation module
│   │   ├── input.json          # Configuration file template
│   │   ├── input_test.json     # Test environment config
│   │   └── input_prod.json     # Production environment config
│   └── samples/
│       └── order_a_coffee_maker.py  # Nova Act sample code
├── releases/
│   └── HƯỚNG_DẪN_SỬ_DỤNG.md   # Vietnamese user guide
├── build/                      # PyInstaller build artifacts
└── dist/                       # Built executables
```

## Code Style Guidelines

- **Language**: Python 3.10+
- **Docstring Style**: Google/NumPy style docstrings
- **Error Handling**: Comprehensive try-catch blocks with user-friendly messages
- **Logging**: Debug-level logging enabled for Nova Act with file output
- **UI**: Vietnamese language for user interface (business requirement)
- **Configuration**: JSON-based with Pydantic validation

## Nova Act Integration

### API Key Configuration
- Configure in `src/config/nova_act_config.py`
- Required environment variable: `NOVA_ACT_API_KEY`
- Production key is hardcoded in config file for built application

### Browser Automation
- **Single Worker Mode**: Application runs with one browser session at a time
- **Headless**: Can be configured for headless operation
- **Logging**: HTML trace files generated for debugging
- **Error Recovery**: Graceful handling of browser automation failures

## Input Configuration

### JSON Schema
```json
{
  "admin_credentials": {
    "username": "admin_username",
    "password": "admin_password", 
    "csp_admin_url": "https://csp-portal.com/portal/users/list"
  },
  "users": [
    {
      "target_user": "user@example.com",
      "new_role": "CSP-RB-TELLER",
      "branch_hierarchy": ["VIB Bank", "North", "002"]
    }
  ]
}
```

### Configuration Files
- `input.json`: Main configuration (must be in same directory as executable)
- `input_test.json`: Test environment template
- `input_prod.json`: Production environment template

## Build & Deployment

### PyInstaller Configuration
- **Build Target**: Single executable file
- **Runtime Hook**: `playwright_runtime_hook.py` for browser dependencies
- **Platforms**: Windows (.exe), macOS, Linux
- **Size**: ~50MB+ (includes Python runtime)

### Deployment Requirements
- Nova Act API key configured
- `input.json` file in same directory as executable
- Internet connection for browser automation
- Sufficient permissions for browser automation

## Testing Instructions

### Manual Testing
1. Run console application: `python console_app.py`
2. Select CSP Admin option (1)
3. Use "View sample format" to generate test input
4. Run automation with test data

### Automated Testing
```bash
# Test the main automation module
cd src/csp
python csp_admin_change_role_and_branch.py --input_file input_test.json
```

### Validation Steps
- Verify Nova Act API key configuration
- Test JSON configuration validation
- Check browser automation with sample data
- Validate built executable functionality

## Security Considerations

### Sensitive Data Handling
- **Passwords**: Never log or display admin passwords
- **API Keys**: Hardcoded in built application, environment variable for development
- **Session Data**: Browser sessions are isolated and cleaned up
- **Logging**: Sensitive information excluded from log files

### Browser Security
- Uses NovaAct's built-in browser isolation
- Single worker mode prevents session conflicts
- Automatic cleanup of temporary browser data

## Error Handling & Debugging

### Common Issues
1. **Missing input.json**: Must be in same directory as executable
2. **Invalid JSON**: Use JSON validator for syntax checking
3. **Nova Act API errors**: Check API key configuration
4. **Browser automation failures**: Check HTML trace files in logs

### Debug Information
- Log files: `csp_automation_[timestamp].log`
- Nova Act traces: HTML files with step-by-step browser actions
- Console output: Real-time status and error messages

## Recent Changes (Refactoring Summary)

### Branch Change Method Consolidation
- **Removed**: `change_bank_user_hierarchical` and `change_user_branch` methods
- **Consolidated**: All branch changes now use `change_user_branch_hierarchical`
- **Added**: `_convert_to_hierarchy` helper for backward compatibility
- **Benefit**: Improved consistency and maintainability

### Single Worker Mode
- **Changed**: From parallel workers to single worker mode
- **Reason**: Enhanced stability and reliability
- **Impact**: Sequential processing of users instead of parallel

## Common Commands

```bash
# Quick start for development
python console_app.py

# Build for distribution
./build.sh  # or build.bat on Windows

# Run automation directly (development)
python -m src.csp.csp_admin_change_role_and_branch --input_file src/csp/input.json

# Check API key configuration
python -c "from src.config.nova_act_config import get_nova_act_api_key; print(get_nova_act_api_key())"

# Generate sample input file
python console_app.py  # Select option 1 → 3 to view sample format
```

## Notes for AI Agents

- The application is designed for Vietnamese banking environment
- UI messages are in Vietnamese for end-user compatibility
- Code comments and documentation are in English
- Configuration follows hierarchical branch structure: Bank → Region → Branch
- Backward compatibility maintained for legacy `new_branch` parameter
- Single worker mode is enforced for production stability
