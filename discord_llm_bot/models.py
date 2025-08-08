from typing import List, Optional
from pydantic import BaseModel, Field


class DiscordConfig(BaseModel):
    """Configuration for Discord bot settings."""
    token: str = Field(..., description="Discord bot token")
    listening_channel_id: Optional[int] = Field(None, description="Default listening channel ID")


class CloudflareConfig(BaseModel):
    """Configuration for Cloudflare AI settings."""
    api_url: str = Field(..., description="Cloudflare AI API URL")
    model: str = Field(..., description="AI model to use")
    context: str = Field(..., description="System context for the AI model")
    token: str = Field(..., description="Cloudflare API token")


class OpenAIConfig(BaseModel):
    """Configuration for OpenAI settings."""
    api_key: str = Field(..., description="OpenAI API key")
    model: str = Field(default="gpt-3.5-turbo", description="OpenAI model to use")
    system_prompt: str = Field(default="", description="System prompt for the AI model")


class BotConfig(BaseModel):
    """Main bot configuration."""
    env: str = Field(default="dev", description="Environment name")
    discord: DiscordConfig
    cloudflare: CloudflareConfig
    openai: Optional[OpenAIConfig] = Field(None, description="OpenAI configuration (optional)")
    ai_provider: str = Field(default="cloudflare", description="AI provider to use (cloudflare or openai)")
    logging_level: str = Field(default="INFO", description="Logging level")


class Message(BaseModel):
    """Represents a Discord message for AI processing."""
    author_name: str = Field(..., description="Name of the message author")
    author_username: str = Field(..., description="Username of the message author")
    content: str = Field(..., description="Message content")
    channel_id: int = Field(..., description="Channel ID where message was sent")
    is_bot: bool = Field(default=False, description="Whether the message is from the bot")


class ConversationContext(BaseModel):
    """Represents the conversation context for AI processing."""
    messages: List[Message] = Field(default_factory=list, description="List of messages in the conversation")
    current_channel_id: Optional[int] = Field(None, description="Current listening channel ID")
    
    def add_message(self, message: Message) -> None:
        """Add a message to the conversation context."""
        self.messages.append(message)
    
    def clear(self) -> None:
        """Clear the conversation context."""
        self.messages.clear()
        self.current_channel_id = None


class AIResponse(BaseModel):
    """Represents an AI-generated response."""
    content: str = Field(..., description="The response content")
    should_stop_listening: bool = Field(default=False, description="Whether to end the conversation and stop listening in the channel")
