"""Tool definitions for the agent template."""

from google.adk.tools import FunctionTool

def example_tool(message: str) -> str:
    """
    An example tool that demonstrates the basic tool structure.
    
    Args:
        message: A message to process
        
    Returns:
        str: The processed message
    """
    return f"Processed: {message}"

def another_example_tool(data: dict) -> dict:
    """
    Another example tool showing data processing.
    
    Args:
        data: Input data dictionary
        
    Returns:
        dict: Processed data with status
    """
    return {
        "status": "success",
        "original_data": data,
        "processed": True
    }

# Create ADK FunctionTool instances
example_function_tool = FunctionTool(func=example_tool)
data_processing_tool = FunctionTool(func=another_example_tool)

# List of all available tools for dynamic discovery
ALL_TOOLS = [
    example_function_tool,
    data_processing_tool,
] 