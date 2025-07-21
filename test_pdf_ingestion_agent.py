#!/usr/bin/env python3
"""Test PDF ingestion agent functionality"""
import requests
import json

def test_pdf_ingestion_agent():
    """Test direct communication with the PDF ingestion agent"""
    
    print("Testing PDF Ingestion Agent directly...")
    payload = {
        "jsonrpc": "2.0",
        "method": "process_task",
        "params": {
            "task_description": "process pdf",
            "parameters": {
                "pdf_path": "/test/path/menu.pdf",
                "document_name": "test_menu.pdf"
            }
        },
        "id": "pdf_ingestion_test"
    }
    
    try:
        response = requests.post(
            "http://localhost:10350/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"PDF Ingestion Agent Status: {response.status_code}")
        print(f"PDF Ingestion Agent Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Parsed result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"PDF Ingestion Agent Error: {e}")

if __name__ == "__main__":
    test_pdf_ingestion_agent() 