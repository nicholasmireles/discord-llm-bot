import logging
import requests
from typing import List, Optional
from abc import ABC, abstractmethod

from pydantic_ai import agent
from ..models import ConversationContext, Message as BotMessage, AIResponse, CloudflareConfig, OpenAIConfig

logger = logging.getLogger(__name__)


class AIService(ABC):
    """Abstract base class for AI services using Pydantic AI."""
    
    @abstractmethod
    async def generate_response(self, context: ConversationContext, current_message: BotMessage) -> AIResponse:
        """Generate a response using the AI service."""
        pass
    
    def format_conversation_messages(
        self, 
        context: ConversationContext, 
        current_message: BotMessage, 
        system_prompt: str
    ) -> List[dict]:
        """
        Format conversation history into a list of messages for AI services.
        
        Args:
            context: The conversation context containing message history
            current_message: The current message to respond to
            system_prompt: The system prompt/context to include
            
        Returns:
            List[dict]: List of formatted messages for AI service consumption
        """
        # Start with system message
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        for msg in context.messages:
            role = "assistant" if msg.is_bot else "user"
            messages.append({
                "role": role,
                "content": f"{msg.author_name}: {msg.content}"
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": f"{current_message.author_name}: {current_message.content}"
        })
        
        return messages


class CloudflareAIService(AIService):
    """Pydantic AI service using Cloudflare Workers AI."""
    
    def __init__(self, config: CloudflareConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.token}",
            "Content-Type": "application/json",
        }

    def check_api_access(self) -> None:
        """Verify that the API access token is valid."""
        test_request = {
            "url": "https://api.cloudflare.com/client/v4/user/tokens/verify",
            "headers": self.headers,
        }
        response = requests.get(**test_request, timeout=30)
        response.raise_for_status()

    async def generate_response(self, context: ConversationContext, current_message: BotMessage) -> AIResponse:
        """
        Generate a response using Cloudflare AI with Pydantic validation.
        
        Args:
            context: The conversation context
            current_message: The current message to respond to
            
        Returns:
            AIResponse: The generated response
        """
        # Format conversation history using common utility
        messages = self.format_conversation_messages(context, current_message, self.config.context)
        
        # Make request to Cloudflare
        request_data = {
            "url": self.config.api_url + self.config.model,
            "headers": self.headers,
            "json": {"messages": messages}
        }
        
        try:
            server_response = requests.post(**request_data)
            
            if server_response.status_code == 200:
                inference = server_response.json()
                response_content = inference["result"]["response"]
                logger.debug(server_response.text)
                
                # Use Pydantic to validate and structure the response
                ai_response = AIResponse(
                    content=response_content,
                    should_stop_listening="$stop" in response_content.lower() or "stop listening" in response_content.lower()
                )
                
                return ai_response
            else:
                logger.error(f"Cloudflare API error: {server_response.status_code} - {server_response.text}")
                return AIResponse(
                    content="I'm sorry, I'm having a hard time thinking right now. :pensive:",
                    should_stop_listening=False
                )
                
        except Exception as e:
            logger.error(f"Error calling Cloudflare AI: {e}")
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
            system_prompt=config.system_prompt
        )

    async def generate_response(self, context: ConversationContext, current_message: BotMessage) -> AIResponse:
        """
        Generate a response using OpenAI with Pydantic AI.
        
        Args:
            context: The conversation context
            current_message: The current message to respond to
            
        Returns:
            AIResponse: The generated response
        """
        try:
            # Format conversation history using common utility
            messages = self.format_conversation_messages(context, current_message, self.config.system_prompt)
            
            # Generate response using Pydantic AI agent
            result = await self.agent.run(messages=messages)
            
            # Extract the response content
            response_content = result.content if hasattr(result, 'content') else str(result)
            
            # Create AIResponse with validation
            ai_response = AIResponse(
                content=response_content,
                should_stop_listening="$stop" in response_content.lower() or "stop listening" in response_content.lower()
            )
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error calling OpenAI with Pydantic AI: {e}")
            return AIResponse(
                content="I'm sorry, I'm having a hard time thinking right now. :pensive:",
                should_stop_listening=False
            )
