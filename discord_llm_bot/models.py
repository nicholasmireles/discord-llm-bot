from typing import Optional
from pydantic import BaseModel, Field


class DiscordConfig(BaseModel):
    """Configuration for Discord bot settings."""

    token: str = Field(..., description="Discord bot token")
    listening_channel_id: Optional[int] = Field(
        None, description="Default listening channel ID"
    )


class AgentConfig(BaseModel):
    """Main bot configuration."""

    api_key: str = Field(..., description="API key")
    api_url: Optional[str] = Field(None, description="API URL")
    model: str = Field(default="gpt-3.5-turbo", description="Model to use")
    system_prompt: str = Field(default="", description="System prompt for the AI model")
    provider: str = Field(
        default="cloudflare", description="AI provider to use (cloudflare or openai)"
    )


class Config(BaseModel):
    """Main bot configuration."""

    env: str = Field(default="dev", description="Environment name")
    logging_level: str = Field(default="INFO", description="Logging level")
    discord: DiscordConfig = Field(..., description="Discord configuration")
    agent: AgentConfig = Field(..., description="Agent configuration")


class AIResponse(BaseModel):
    """Represents an AI-generated response."""

    content: str = Field(..., description="The response content")
    should_stop_listening: bool = Field(
        default=False,
        description="Whether to end the conversation and stop listening in the channel",
    )
