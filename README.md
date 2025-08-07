# Discord Chat Bot with Pydantic AI

A modern Discord chat bot that uses Pydantic AI for structured, type-safe AI interactions. The bot can work with multiple AI providers including Cloudflare Workers AI and OpenAI.

## Features

- **Pydantic AI Integration**: Uses Pydantic AI for structured, type-safe AI responses
- **Multiple AI Providers**: Support for Cloudflare Workers AI and OpenAI
- **Type Safety**: Full type safety with Pydantic models
- **Conversation Context**: Maintains conversation history and context
- **Flexible Configuration**: Easy configuration through YAML files and environment variables

## Migration from Original Bot

This project has been migrated to use Pydantic AI, providing:

1. **Better Type Safety**: All AI interactions are now type-safe with Pydantic models
2. **Structured Responses**: AI responses are validated and structured using Pydantic
3. **Multiple AI Providers**: Easy switching between different AI services
4. **Improved Error Handling**: Better error handling and validation
5. **Modern Architecture**: Clean separation of concerns with service-based architecture

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   uv sync
   ```

## Configuration

### Environment Variables

- `DISCORD_TOKEN`: Your Discord bot token
- `CLOUDFLARE_TOKEN`: Your Cloudflare API token (if using Cloudflare)
- `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI)
- `ENV`: Environment name (default: "dev")

### Configuration Files

The bot uses YAML configuration files in the `config/` directory:

- `config/default.yaml`: Default configuration
- `config/dev.yaml`: Development environment configuration

Example configuration:
```yaml
env: dev
discord:
  token: ""  # Loaded from environment variable
cloudflare:
  api_url: "https://api.cloudflare.com/client/v4/accounts/.../ai/run/"
  model: "@cf/meta/llama-2-7b-chat-fp16"
  context: "You are NickBot, a friendly Discord bot assistant..."
  token: ""  # Loaded from environment variable
openai:
  api_key: ""  # Loaded from environment variable
  model: "gpt-3.5-turbo"
  system_prompt: "You are NickBot, a friendly Discord bot assistant..."
ai_provider: "cloudflare"  # Options: "cloudflare" or "openai"
logging_level: "INFO"
```

## Usage

### Running the Bot

```bash
uv run python -m discord_llm_bot
```

### Bot Commands

- **Mention the bot**: Start a conversation by mentioning the bot
- **Continue chatting**: The bot will continue responding in the same channel
- **$stop**: Stop the conversation and clear context

## Architecture

### Core Components

1. **Models** (`models.py`): Pydantic models for type safety
2. **AI Services** (`lib/pydantic_ai_service.py`): Pydantic AI service implementations
3. **Client** (`client.py`): Discord bot client with conversation management
4. **Configuration** (`config.py`): Configuration loading and validation

### AI Service Architecture

The bot uses Pydantic AI for all AI interactions:

- **CloudflareAIService**: Cloudflare with Pydantic AI validation
- **OpenAIAIService**: OpenAI with Pydantic AI structured responses

## Benefits of Pydantic AI Migration

1. **Type Safety**: All AI interactions are validated with Pydantic models
2. **Structured Responses**: AI responses are guaranteed to match expected structure
3. **Better Error Handling**: Validation errors are caught and handled gracefully
4. **Developer Experience**: Better IDE support and autocomplete
5. **Maintainability**: Cleaner, more maintainable code structure

## Development

### Adding New AI Providers

1. Create a new service class implementing the `AIService` interface
2. Add configuration models in `models.py`
3. Update the main entry point to support the new provider

### Testing

The bot includes comprehensive error handling and logging. Check the logs for debugging information.

## License

This project is licensed under the MIT License.
