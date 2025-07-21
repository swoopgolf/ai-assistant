"""Tool definitions for the pdf-ingestion-agent."""

import json
import os
from typing import List, Dict, Any

import google.generativeai as genai
from google.adk.tools import FunctionTool

from common_utils.database import get_database_manager

db_manager = get_database_manager()

def extract_menu_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract structured menu items from PDF using Google Gemini.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of dicts with item details
    """
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    uploaded_file = genai.upload_file(pdf_path)
    
    prompt = """
    Extract all menu items from this document. 
    Output as a JSON array of objects, each with:
    - name: string (required)
    - price: number (required)
    - description: string (optional)
    - category: string (optional)
    - allergens: array of strings (optional)
    Ensure the output is valid JSON only.
    """
    
    response = model.generate_content([uploaded_file, prompt])
    
    try:
        items = json.loads(response.text.strip().removeprefix("```json").removesuffix("```"))
        return items
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON response from Gemini")

def validate_extracted_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate and clean extracted items.
    
    Args:
        items: List of extracted items
        
    Returns:
        Validated list of items
    """
    validated = []
    for item in items:
        if "name" in item and isinstance(item["name"], str) and "price" in item and isinstance(item["price"], (int, float)):
            validated.append(item)
    return validated

def categorize_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Assign categories if not present.
    
    Args:
        items: List of items
        
    Returns:
        Items with categories
    """
    for item in items:
        if "category" not in item or not item["category"]:
            item["category"] = "Uncategorized"
    return items

def insert_menu_items(items: List[Dict[str, Any]], document_name: str) -> Dict[str, int]:
    """
    Insert validated items into database and log import.
    
    Args:
        items: List of items to insert
        document_name: Name of the source document
        
    Returns:
        Report of insertion results
    """
    report = {"imported": 0, "skipped": 0, "failed": 0}
    failed_details = []
    
    for item in items:
        try:
            # Get or create category
            cat_query = "SELECT id FROM categories WHERE name = %s"
            cat_result = db_manager.execute_query(cat_query, (item["category"],))
            
            if not cat_result:
                insert_cat = "INSERT INTO categories (name) VALUES (%s) RETURNING id"
                cat_id = db_manager.execute_query(insert_cat, (item["category"],))[0]["id"]
            else:
                cat_id = cat_result[0]["id"]
            
            # Insert item
            insert_query = """
                INSERT INTO items (name, price, description, category_id, allergens, disabled)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (
                item["name"],
                item["price"],
                item.get("description", ""),
                cat_id,
                json.dumps(item.get("allergens", [])),
                False
            )
            db_manager.execute_insert(insert_query, params)
            report["imported"] += 1
        except Exception as e:
            report["failed"] += 1
            failed_details.append(str(e))
    
    # Log import
    log_query = """
        INSERT INTO import_log 
        (document_name, document_path, items_found, items_imported, items_skipped, 
         items_failed, import_status, error_details, club_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    log_params = (
        document_name,
        "",  # document_path if available
        len(items),
        report["imported"],
        report["skipped"],
        report["failed"],
        "completed" if report["failed"] == 0 else "partial",
        json.dumps(failed_details),
        1  # Assuming club_id 1, adjust as needed
    )
    db_manager.execute_insert(log_query, log_params)
    
    return report

def generate_import_report(report: Dict[str, int]) -> str:
    """
    Generate formatted import report.
    
    Args:
        report: Insertion report
        
    Returns:
        Formatted string report
    """
    return f"Import Report: Imported {report['imported']}, Skipped {report['skipped']}, Failed {report['failed']}"

# Create FunctionTool instances
extract_menu_tool = FunctionTool(func=extract_menu_from_pdf)
validate_items_tool = FunctionTool(func=validate_extracted_items)
categorize_items_tool = FunctionTool(func=categorize_items)
insert_items_tool = FunctionTool(func=insert_menu_items)
generate_report_tool = FunctionTool(func=generate_import_report)

# List of all available tools
ALL_TOOLS = [
    extract_menu_tool,
    validate_items_tool,
    categorize_items_tool,
    insert_items_tool,
    generate_report_tool,
] 