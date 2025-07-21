# Classification Agent

The Classification Agent is responsible for analyzing user queries and determining which specialized agent should handle the request. It uses AI-powered classification logic to categorize requests and return structured output for routing decisions.

## Features

- AI-powered query classification using OpenAI GPT models
- Structured output for routing decisions
- Support for multiple query types (menu, order history, price updates, etc.)
- Context-aware classification with conversation history
- Fallback classification for error handling

## Supported Query Types

- `menu_inquiry`: Questions about menu items, categories, availability
- `order_history`: Requests for past order information
- `price_update`: Requests to modify item prices
- `pdf_ingestion`: Document processing and data extraction
- `general`: General queries that don't fit specific categories

## Configuration

The agent requires OpenAI API credentials to be configured in the environment:

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

## Running the Agent

```bash
python -m classification_agent
```

The agent will start on port 10300 by default. 