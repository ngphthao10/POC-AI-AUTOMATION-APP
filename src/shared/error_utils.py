"""
Error handling utilities for cleaner error messages
"""
import logging

logger = logging.getLogger(__name__)


def extract_error_message(error_str: str) -> str:
    """
    Extract clean error message from complex error objects.

    Handles formats like:
    - ActAgentError(message = The actual error\n  metadata = ...)
    - Standard exceptions
    - Multiline errors

    Args:
        error_str: Raw error string

    Returns:
        Clean, user-friendly error message
    """
    if not error_str:
        return "Unknown error"

    error_str = str(error_str).strip()

    # Check if it's an ActAgentError format
    if error_str.startswith("ActAgentError("):
        try:
            lines = error_str.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('message = '):
                    # Extract the message part after "message = "
                    message = line[10:].strip()
                    return message
        except Exception as e:
            logger.warning(f"Failed to parse ActAgentError format: {e}")

    # Check for other common error patterns
    if "message:" in error_str.lower():
        try:
            parts = error_str.split("message:", 1)
            if len(parts) > 1:
                message = parts[1].strip()
                # Remove any trailing metadata
                for delimiter in ['\n', 'metadata', 'session_id', 'act_id']:
                    if delimiter in message:
                        message = message.split(delimiter)[0].strip()
                return message
        except Exception as e:
            logger.warning(f"Failed to parse message: format: {e}")

    # Default: return first line
    first_line = error_str.split('\n')[0].strip()
    return first_line if first_line else error_str


def is_timeout_error(error: Exception) -> bool:
    """
    Check if error is a timeout error.

    Args:
        error: Exception object

    Returns:
        True if timeout error
    """
    error_str = str(error).lower()
    return (
        'timeout' in error_str or
        'timeouterror' in error_str or
        'timed out' in error_str
    )


def is_network_error(error: Exception) -> bool:
    """
    Check if error is a network error.

    Args:
        error: Exception object

    Returns:
        True if network error
    """
    error_str = str(error).lower()
    return (
        'connection' in error_str or
        'network' in error_str or
        'unreachable' in error_str or
        'refused' in error_str
    )


def format_error_for_display(error: Exception, context: str = "") -> str:
    """
    Format error for user-friendly display.

    Args:
        error: Exception object
        context: Context string (e.g., "Login failed")

    Returns:
        Formatted error message
    """
    clean_msg = extract_error_message(str(error))

    if is_timeout_error(error):
        error_type = "⏱️ Timeout"
    elif is_network_error(error):
        error_type = "🌐 Network Error"
    else:
        error_type = "❌ Error"

    if context:
        return f"{error_type} ({context}): {clean_msg}"
    else:
        return f"{error_type}: {clean_msg}"
