import requests

from ..config import AgentConfig


def check_cloudflare_api_access(config: AgentConfig) -> None:
    """Verify that the Cloudflare API access token is valid."""
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
    }
    test_request = {
        "url": "https://api.cloudflare.com/client/v4/user/tokens/verify",
        "headers": headers,
    }
    response = requests.get(**test_request, timeout=30)
    response.raise_for_status()
