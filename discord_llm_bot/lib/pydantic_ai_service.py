import logging
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse
from pydantic_ai.models import Model, StreamedResponse
import requests
from typing import List, Optional, AsyncIterator, Union
import json

from pydantic_ai import agent
from ..models import Message as BotMessage, AIResponse, CloudflareConfig, OpenAIConfig

logger = logging.getLogger(__name__)


class CloudflareModel(Model):
    """Custom Pydantic AI Model for Cloudflare Workers AI."""
    
    def __init__(self, config: CloudflareConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.token}",
            "Content-Type": "application/json",
        }
    
    async def request(self, messages: List[ModelMessage]) -> ModelResponse:
        """Send a request to Cloudflare AI and return the response."""
        
        # Convert ModelMessage objects to the format expected by Cloudflare API
        cf_messages = []
        for msg in messages:
            if hasattr(msg, 'role') and hasattr(msg, 'content'):
                cf_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        request_data = {
            "url": self.config.api_url + self.config.model,
            "headers": self.headers,
            "json": {"messages": cf_messages}
        }
        
        try:
            response = requests.post(**request_data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            response_content = result.get("result", {}).get("response", "")
            
            # Return a ModelResponse object
            return ModelResponse(
                model_name=self.config.model,
                content=response_content
            )
            
        except Exception as e:
            logger.error(f"Error calling Cloudflare AI: {e}")
            # Return error response
            return ModelResponse(
                model_name=self.config.model,
                content="I'm sorry, I'm having a hard time thinking right now. :pensive:"
            )
    
    async def stream(self, messages: List[ModelMessage]) -> AsyncIterator[str]:
        """Stream response from Cloudflare AI (not implemented for Cloudflare)."""
        # Cloudflare AI doesn't support streaming, so we'll just yield the full response
        response = await self.request(messages)
        yield response.content
    
    def name(self) -> str:
        """Return the model name."""
        return f"cloudflare:{self.config.model}"


def check_cloudflare_api_access(config: CloudflareConfig) -> None:
    """Verify that the Cloudflare API access token is valid."""
    headers = {
        "Authorization": f"Bearer {config.token}",
        "Content-Type": "application/json",
    }
    test_request = {
        "url": "https://api.cloudflare.com/client/v4/user/tokens/verify",
        "headers": headers,
    }
    response = requests.get(**test_request, timeout=30)
    response.raise_for_status()


def create_cloudflare_agent(config: CloudflareConfig) -> agent.Agent:
    """Create a Pydantic AI agent for Cloudflare AI."""
    custom_model = CloudflareModel(config)
    return agent.Agent(
        model=custom_model,
        system_prompt=config.context,
        output_type=AIResponse
    )


def create_openai_agent(config: OpenAIConfig) -> agent.Agent:
    """Create a Pydantic AI agent for OpenAI."""
    return agent.Agent(
        model=config.model,
        system_prompt=config.system_prompt,
        output_type=AIResponse
    )