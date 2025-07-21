# Pdf Ingestion Agent

Specialized agent for extracting menu items and data from PDF documents, processing unstructured content, and inserting new items into the database

## Overview

This agent is part of the multi-agent framework and provides specialized functionality for specialized agent for extracting menu items and data from pdf documents, processing unstructured content, and inserting new items into the database.

## Features

- Pdf Text Extraction
- Ocr Processing
- Menu Item Parsing
- Structured Data Extraction
- Document Analysis
- Data Validation
- Bulk Item Insertion
- Format Detection
- Import Reporting

## Configuration

- **Port**: 10350
- **Agent Name**: pdf-ingestion-agent
- **Version**: 1.0.0

## Usage

To start this agent:

```bash
cd pdf-ingestion-agent
python -m pdf_ingestion_agent
```

## Health Check

```bash
curl http://localhost:10350/health
```

## Integration

This agent is automatically registered with the orchestrator and can be accessed through the A2A communication protocol.

## Development

- **Author**: Club Management System <dev@clubmanagement.com>
- **Created**: 2025-07-20
- **Framework Version**: 2.0.0

## License

Apache License 2.0
