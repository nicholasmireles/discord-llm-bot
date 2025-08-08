# Discord Chat Bot with Pydantic AI

A modern Discord chat bot that uses Pydantic AI for structured, type-safe AI interactions. The bot can work with multiple AI providers including Cloudflare Workers AI and OpenAI.

## Features

- **Pydantic AI Integration**: Uses Pydantic AI for structured, type-safe AI responses
- **Multiple AI Providers**: Support for Cloudflare Workers AI and OpenAI
- **Type Safety**: Full type safety with Pydantic models
- **Conversation Context**: Maintains conversation history and context
- **Flexible Configuration**: Easy configuration through YAML files and environment variables

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   uv sync
   ```

## Configuration

### Environment Variables

- `DISCORD_TOKEN`: Your Discord bot token
- `AGENT_API_KEY`: Your Cloudflare API or OpenAI API key
- `ENV`: Environment name (default: "dev")

### Configuration Files

The bot uses YAML configuration files in the `config/` directory:

- `config/default.yaml`: Default configuration
- `config/{$ENV}.yaml`: Environment-specific configurations

Example configuration:
```yaml
env: dev
logging_level: "INFO"
discord:
  token: ""  # Loaded from environment variable
agent:
  api_url: "https://api.cloudflare.com/client/v4/accounts/.../ai/run/"
  api_key: ""  # Loaded from environment variable
  model: "@cf/meta/llama-2-7b-chat-fp16"
  system_prompt: "You are NickBot, a friendly Discord bot assistant..."
  provider: "cloudflare"  # Options: "cloudflare" or "openai"
```

## Usage

### Running the Bot

```bash
uv run python -m discord_llm_bot
```

### Conversation Flow

- **Mention the bot**: Start a conversation by mentioning the bot
- **Continue chatting**: The bot will continue responding in the same channel
- **End the conversation**: The bot has the ability to end the conversation each time it replies.

## Architecture

### Core Components

1. **Models** (`models.py`): Pydantic models for type safety
2. **Agent** (`lib/agent.py`): Pydantic AI Agent generation and custom model definitions
3. **Client** (`client.py`): Discord bot client with conversation management
4. **Configuration** (`config.py`): Configuration loading and validation

### AI Service Architecture

The bot uses Pydantic AI for all AI interactions:

- **CloudflareAIService**: Cloudflare with Pydantic AI validation
- **OpenAIAIService**: OpenAI with Pydantic AI structured responses

## Development

### Adding New AI Providers

1. Create a new service class implementing the `AIService` interface
2. Add configuration models in `models.py`
3. Update the main entry point to support the new provider

### Testing

The bot includes comprehensive error handling and logging. Check the logs for debugging information.

## License

This project is licensed under the MIT License.
