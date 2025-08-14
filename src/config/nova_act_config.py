"""
Nova Act Configuration
This file contains the Nova Act API key configuration for the built application.
"""

# Replace 'your_nova_act_api_key_here' with your actual Nova Act API key
NOVA_ACT_API_KEY = "667f1144-738f-4c84-acce-f07ed3cb1661"

def get_nova_act_api_key():
    """
    Get the Nova Act API key from configuration.
    Returns the hardcoded API key for use in the built application.
    """
    if NOVA_ACT_API_KEY == "your_nova_act_api_key_here":
        raise ValueError(
            "Nova Act API key not configured. Please update the NOVA_ACT_API_KEY "
            "value in src/config/nova_act_config.py with your actual API key."
        )
    return NOVA_ACT_API_KEY
