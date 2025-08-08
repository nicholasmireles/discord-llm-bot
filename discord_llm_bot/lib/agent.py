import logging
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart
from pydantic_ai.models import Model
import requests
from typing import List, AsyncIterator

from pydantic_ai import agent
from ..models import AIResponse, AgentConfig

logger = logging.getLogger(__name__)


class CloudflareModel(Model):
    """Custom Pydantic AI Model for Cloudflare Workers AI."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }

    async def request(self, messages: List[ModelMessage]) -> ModelResponse:
        """Send a request to Cloudflare AI and return the response."""

        # Convert ModelMessage objects to the format expected by Cloudflare API
        cf_messages = []
        for msg in messages:
            cf_messages.extend(
                [
                    {
                        "role": "user" if msg.kind == "request" else "system",
                        "content": part.content,
                    }
                    for part in msg.parts
                    if isinstance(part, TextPart)
                ]
            )

        request_data = {
            "url": self.config.api_url + self.config.model,
            "headers": self.headers,
            "json": {"messages": cf_messages},
        }

        response = requests.post(**request_data, timeout=30)
        response.raise_for_status()

        result = response.json()
        response_content = result.get("result", {}).get("response", "")

        # Return a ModelResponse object
        return ModelResponse(model_name=self.config.model, content=response_content)

    async def stream(self, messages: List[ModelMessage]) -> AsyncIterator[str]:
        """Stream response from Cloudflare AI (not implemented for Cloudflare)."""
        # Cloudflare AI doesn't support streaming, so we'll just yield the full response
        response = await self.request(messages)
        yield response.content

    def name(self) -> str:
        """Return the model name."""
        return f"cloudflare:{self.config.model}"


def create_ai_agent(agent_config: AgentConfig) -> agent.Agent:
    """Create a Pydantic AI agent based on the bot configuration."""
    if agent_config.ai_provider == "cloudflare":
        model = CloudflareModel(agent_config)
    else:
        model = agent_config.model

    return agent.Agent(
        model=model, system_prompt=agent_config.system_prompt, output_type=AIResponse
    )
