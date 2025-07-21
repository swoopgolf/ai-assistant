# Price Update Agent

Specialized agent for executing menu price updates, item modifications, and availability changes through natural language commands with database write operations

## Overview

This agent is part of the multi-agent framework and provides specialized functionality for specialized agent for executing menu price updates, item modifications, and availability changes through natural language commands with database write operations.

## Features

- Price Updates
- Menu Editing
- Item Modifications
- Availability Management
- Bulk Price Changes
- Category Adjustments
- Promotional Pricing
- Audit Logging
- Change Validation

## Configuration

- **Port**: 10410
- **Agent Name**: price-update-agent
- **Version**: 1.0.0

## Usage

To start this agent:

```bash
cd price-update-agent
python -m price_update_agent
```

## Health Check

```bash
curl http://localhost:10410/health
```

## Integration

This agent is automatically registered with the orchestrator and can be accessed through the A2A communication protocol.

## Development

- **Author**: Club Management System <dev@clubmanagement.com>
- **Created**: 2025-07-20
- **Framework Version**: 2.0.0

## License

Apache License 2.0
