"""
Pdf Ingestion Agent Executor
Executor for the pdf-ingestion-agent agent.
"""

import logging
from typing import Dict, Any

import sys
from pathlib import Path

# Add parent directory for common_utils access
parent_dir = Path(__file__).resolve().parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from common_utils.data_handle_manager import get_data_handle_manager
from .tools import (
    extract_menu_from_pdf,
    validate_extracted_items,
    categorize_items,
    insert_menu_items,
    generate_import_report
)

logger = logging.getLogger(__name__)

class AgentExecutor:
    """
    PDF Ingestion Agent executor with specialized functionality for processing PDFs using Gemini.
    """
    
    def __init__(self):
        self.data_manager = get_data_handle_manager()
        logger.info("PDF Ingestion Agent initialized")

    async def process_task_skill(self, task_description: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main processing skill for PDF ingestion.
        
        Args:
            task_description: Description of the task (e.g., "ingest_pdf")
            parameters: Parameters including "pdf_path" and "document_name"
            
        Returns:
            Dict containing the result of the task processing
        """
        try:
            logger.info(f"Processing task: {task_description}")
            
            if parameters is None:
                parameters = {}
            
            task_lower = task_description.lower()
            
            if "ingest" in task_lower or "process pdf" in task_lower:
                pdf_path = parameters.get("pdf_path")
                document_name = parameters.get("document_name", "unnamed.pdf")
                
                if not pdf_path:
                    raise ValueError("pdf_path is required")
                
                # Extraction with retry
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        items = extract_menu_from_pdf(pdf_path)
                        break
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise
                        logger.warning(f"Retry {attempt+1}/{max_retries} for extraction: {str(e)}")
                
                validated = validate_extracted_items(items)
                categorized = categorize_items(validated)
                report = insert_menu_items(categorized, document_name)
                formatted_report = generate_import_report(report)
                
                return {
                    "status": "success",
                    "report": report,
                    "formatted": formatted_report
                }
            else:
                raise ValueError(f"Unknown task: {task_description}")
            
        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to process task"
            }

    async def get_capabilities_skill(self) -> Dict[str, Any]:
        """
        Returns the capabilities of this agent.
        
        Returns:
            Dict describing agent capabilities
        """
        return {
            "agent_type": "specialized",
            "capabilities": [
                "process_task_skill",
                "get_capabilities_skill"
            ],
            "description": "Specialized agent for extracting menu items from PDF documents using Google Gemini and inserting into the database",
            "version": "1.0.0"
        } 