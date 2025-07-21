# Menu Qa Agent

Specialized agent for answering questions about current menu items, availability, pricing, ingredients, and dietary restrictions

## Overview

This agent is part of the multi-agent framework and provides specialized functionality for specialized agent for answering questions about current menu items, availability, pricing, ingredients, and dietary restrictions.

## Features

- Menu Queries
- Item Lookup
- Price Inquiry
- Availability Check
- Dietary Information
- Ingredient Search
- Category Browsing
- Menu Navigation

## Configuration

- **Port**: 10220
- **Agent Name**: menu-qa-agent
- **Version**: 1.0.0

## Usage

To start this agent:

```bash
cd menu-qa-agent
python -m menu_qa_agent
```

## Health Check

```bash
curl http://localhost:10220/health
```

## Integration

This agent is automatically registered with the orchestrator and can be accessed through the A2A communication protocol.

## Development

- **Author**: Club Management System <dev@clubmanagement.com>
- **Created**: 2025-07-20
- **Framework Version**: 2.0.0

## License

Apache License 2.0
