from datetime import datetime, timezone


def datetime_tool(query: str = "") -> str:
    """Return current date, time, and timezone information."""
    now = datetime.now(timezone.utc)
    return (
        f"Current UTC datetime: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
        f"Day: {now.strftime('%A')}\n"
        f"Unix timestamp: {int(now.timestamp())}"
    )
