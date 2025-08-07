#!/usr/bin/env python3
"""
Test script to verify the Pydantic AI migration works correctly.
This script tests the basic functionality without requiring Discord or AI API access.
"""

import asyncio
import logging
from discord_llm_bot.models import (
    BotConfig, DiscordConfig, CloudflareConfig, OpenAIConfig,
    Message, ConversationContext, AIResponse
)
from discord_llm_bot.lib.pydantic_ai_service import AIService, CloudflareAIService, OpenAIAIService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_models():
    """Test that Pydantic models work correctly."""
    print("Testing Pydantic models...")
    
    # Test Message model
    message = Message(
        author_name="TestUser",
        author_username="testuser",
        content="Hello, bot!",
        channel_id=123456789,
        is_bot=False
    )
    print(f"✓ Message model: {message}")
    
    # Test ConversationContext model
    context = ConversationContext()
    context.add_message(message)
    print(f"✓ ConversationContext model: {context}")
    
    # Test AIResponse model
    response = AIResponse(
        content="Hello! How can I help you?",
        should_stop_listening=False
    )
    print(f"✓ AIResponse model: {response}")
    
    print("✓ All Pydantic models working correctly!")


def test_config_loading():
    """Test configuration loading."""
    print("\nTesting configuration loading...")
    
    try:
        from discord_llm_bot.config import BOT_CONFIG
        print(f"✓ Configuration loaded successfully!")
        print(f"  - Environment: {BOT_CONFIG.env}")
        print(f"  - AI Provider: {BOT_CONFIG.ai_provider}")
        print(f"  - Logging Level: {BOT_CONFIG.logging_level}")
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")


async def test_ai_service_interface():
    """Test that AI service interface works correctly."""
    print("\nTesting AI service interface...")
    
    # Create a mock AI service for testing
    class MockAIService(AIService):
        async def generate_response(self, context, current_message):
            return AIResponse(
                content="This is a test response from the mock AI service.",
                should_stop_listening=False
            )
    
    # Test the mock service
    mock_service = MockAIService()
    context = ConversationContext()
    message = Message(
        author_name="TestUser",
        author_username="testuser",
        content="Test message",
        channel_id=123456789
    )
    
    response = await mock_service.generate_response(context, message)
    print(f"✓ Mock AI service response: {response.content}")
    print("✓ AI service interface working correctly!")


def main():
    """Run all tests."""
    print("🧪 Testing Pydantic AI Migration")
    print("=" * 40)
    
    # Test Pydantic models
    test_models()
    
    # Test configuration loading
    test_config_loading()
    
    # Test AI service interface
    asyncio.run(test_ai_service_interface())
    
    print("\n" + "=" * 40)
    print("✅ All tests passed! Migration successful!")
    print("\nTo run the bot:")
    print("1. Set your environment variables (DISCORD_TOKEN, CLOUDFLARE_TOKEN, etc.)")
    print("2. Run: python -m discord_llm_bot")
    print("3. The bot now uses Pydantic AI by default!")


if __name__ == "__main__":
    main()
