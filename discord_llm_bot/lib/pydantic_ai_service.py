import logging
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse
from pydantic_ai.models import Model, StreamedResponse
import requests
from typing import List, Optional, AsyncIterator, Union
from abc import ABC, abstractmethod
import json

from pydantic_ai import agent
from ..models import ConversationContext, Message as BotMessage, AIResponse, CloudflareConfig, OpenAIConfig

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


class AIService(ABC):
    """Abstract base class for AI services using Pydantic AI."""

    message_history: List[ModelMessage] = []
    
    @abstractmethod
    async def generate_response(self, current_message: BotMessage) -> AIResponse:
        """Generate a response using the AI service."""
        pass

class CloudflareAIService(AIService):
    """Pydantic AI service using Cloudflare Workers AI with custom model."""
    
    def __init__(self, config: CloudflareConfig):
        self.config = config
        self.custom_model = CloudflareModel(config)
        # Create a Pydantic AI agent with our custom model
        self.agent = agent.Agent(
            model=self.custom_model,
            system_prompt=config.context,
            output_type=AIResponse
        )

    def check_api_access(self) -> None:
        """Verify that the API access token is valid."""
        headers = {
            "Authorization": f"Bearer {self.config.token}",
            "Content-Type": "application/json",
        }
        test_request = {
            "url": "https://api.cloudflare.com/client/v4/user/tokens/verify",
            "headers": headers,
        }
        response = requests.get(**test_request, timeout=30)
        response.raise_for_status()

    async def generate_response(self, current_message: BotMessage) -> AIResponse:
        """
        Generate a response using Cloudflare AI with Pydantic AI and custom model.
        
        Args:
            current_message: The current message to respond to
            
        Returns:
            AIResponse: The generated response
        """
        try:
            # Generate response using Pydantic AI agent with custom model
            result: agent.AgentRunResult = await self.agent.run(
                user_prompt=current_message.content,
                message_history=self.message_history
            )

            # Check if we should stop listening and clear history
            if result.output.should_stop_listening:
                self.message_history.clear()
            else:
                self.message_history.extend(result.new_messages())

            return result.output
            
        except Exception as e:
            logger.error(f"Error calling Cloudflare AI with Pydantic AI: {e}")
            return AIResponse(
                content="I'm sorry, I'm having a hard time thinking right now. :pensive:",
                should_stop_listening=False
            )


class OpenAIAIService(AIService):
    """Pydantic AI service using OpenAI API."""
    
    def __init__(self, config: OpenAIConfig):
        self.config = config
        # Create a Pydantic AI agent for OpenAI
        self.agent = agent.Agent(
            model=config.model,
            system_prompt=config.system_prompt,
            output_type=AIResponse
        )

    async def generate_response(self, current_message: BotMessage) -> AIResponse:
        """
        Generate a response using OpenAI with Pydantic AI.
        
        Args:
            current_message: The current message to respond to
            
        Returns:
            AIResponse: The generated response
        """
        try:
            # Generate response using Pydantic AI agent
            result: agent.AgentRunResult = await self.agent.run(messages=self.message_history)

            if result.output.should_stop_listening:
                self.message_history.clear()
            else:
                self.message_history.extend(result.new_messages())

            return result.output
            
        except Exception as e:
            logger.error(f"Error calling OpenAI with Pydantic AI: {e}")
            return AIResponse(
                content="I'm sorry, I'm having a hard time thinking right now. :pensive:",
                should_stop_listening=False
            )
