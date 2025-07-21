#!/usr/bin/env python3
"""
PDF Ingestion Agent - A2A Server Implementation
"""

import logging
import sys
from pathlib import Path

# Add the parent directory to sys.path to make common_utils accessible
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from common_utils import create_agent_server
from .agent_executor import AgentExecutor

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the PDF ingestion agent."""
    logging.basicConfig(level=logging.INFO)
    logger.info("🤖 Starting PDF Ingestion Agent A2A Server")
    logger.info("🔧 Specialized agent: Extracts menu items from PDFs using Google Gemini and inserts into database")

    # Create executor
    executor = AgentExecutor()

    # Create standardized agent server
    server = create_agent_server(
        executor=executor,
        agent_name="pdf_ingestion_agent",
        title="PDF Ingestion Agent",
        port=10350,
        agent_description="Specialized agent for extracting menu items from PDF documents using Google Gemini and inserting into the database",
        version="v1.0",
        custom_health_data={
            "agent_type": "specialized",
            "supported_operations": [
                ["extract_menu_from_pdf", "validate_extracted_items", "categorize_items", "insert_menu_items", "generate_import_report"]
            ]
        }
    )

    # Run the server
    server.run()

if __name__ == "__main__":
    main() 