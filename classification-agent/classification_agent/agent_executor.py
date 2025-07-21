#!/usr/bin/env python3
"""
Classification Agent Executor
"""

import logging
import os
import json
import time
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class ClassificationAgentExecutor:
    """
    Main executor for the classification agent.
    Handles query classification and routing decisions.
    """
    
    def __init__(self):
        """Initialize the classification agent executor."""
        logger.info("Initializing ClassificationAgentExecutor")
        
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        
        # Model configuration
        self.model = "gpt-4o-mini"
        self.temperature = 0.1
        
        # Classification cache
        self._classification_cache = {}
        
        # Initialize supported query types and their corresponding agents
        self.agent_mapping = {
            "menu_inquiry": "menu-qa-agent",
            "order_history": "order-history-qa-agent", 
            "price_update": "price-update-agent",
            "pdf_ingestion": "pdf-ingestion-agent",
            "general": "menu-qa-agent"  # Default to menu agent for general queries
        }
        
        # Initialize database schema for context
        self.db_schema = {
            "orders": [
                "id", "created_at", "updated_at", "deleted_at", "customer_id", "vendor_id",
                "location_id", "status", "total", "tax", "instructions", "type", "marker_id",
                "fee", "loyalty_id", "fee_percent", "tip"
            ],
            "order_items": [
                "id", "created_at", "updated_at", "deleted_at", "item_id", "quantity",
                "order_id", "instructions"
            ],
            "items": [
                "id", "created_at", "updated_at", "deleted_at", "name", "description",
                "price", "category_id", "disabled", "seq_num"
            ],
            "categories": [
                "id", "created_at", "updated_at", "deleted_at", "name", "description",
                "menu_id", "disabled", "start_time", "end_time", "seq_num"
            ],
            "menus": [
                "id", "created_at", "updated_at", "deleted_at", "name", "description",
                "location_id", "disabled"
            ],
            "options": [
                "id", "created_at", "updated_at", "deleted_at", "name", "description",
                "min", "max", "item_id", "disabled"
            ],
            "option_items": [
                "id", "created_at", "updated_at", "deleted_at", "name", "description",
                "price", "option_id", "disabled"
            ],
            "locations": [
                "id", "created_at", "updated_at", "deleted_at", "name", "description",
                "timezone", "latitude", "longitude", "active", "disabled", "code", "tax_rate", "settings"
            ],
            "users": [
                "id", "created_at", "updated_at", "deleted_at", "first_name", "last_name",
                "email", "picture", "phone"
            ]
        }
        
        logger.info("ClassificationAgentExecutor initialized successfully")
    
    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a classification request.
        
        Args:
            request: The request data containing the query to classify
            
        Returns:
            Classification result with routing information
        """
        try:
            # Extract the query from the request
            query = request.get("query", "")
            conversation_context = request.get("conversation_context", {})
            use_cache = request.get("use_cache", True)
            
            if not query:
                return self._create_error_response("No query provided")
            
            logger.info(f"Classifying query: {query}")
            
            # Perform classification
            classification_result = self.classify_query(
                query=query,
                conversation_context=conversation_context,
                use_cache=use_cache
            )
            
            # Add routing information
            query_type = classification_result.get("query_type", "general")
            target_agent = self.agent_mapping.get(query_type, "menu-qa-agent")
            
            # Create response with routing information
            response = {
                "success": True,
                "classification": classification_result,
                "routing": {
                    "target_agent": target_agent,
                    "query_type": query_type,
                    "confidence": classification_result.get("confidence", 0.0)
                },
                "timestamp": time.time()
            }
            
            logger.info(f"Classification completed. Target agent: {target_agent}")
            return response
            
        except Exception as e:
            logger.error(f"Error executing classification request: {str(e)}")
            return self._create_error_response(str(e))
    
    def classify_query(
        self, 
        query: str,
        conversation_context: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Classify a user query to determine its type and extract parameters.
        
        Args:
            query: The user's query text
            conversation_context: Optional conversation context for better classification
            use_cache: Whether to use cached results
            
        Returns:
            Classification result dictionary
        """
        # Check cache first
        if use_cache:
            cached_result = self._check_cache(query)
            if cached_result:
                logger.debug(f"Using cached classification for query: {query}")
                return cached_result
        
        # If no OpenAI client, use fallback classification
        if not self.client:
            logger.warning("No OpenAI client available, using fallback classification")
            return self._fallback_classification(query)
        
        try:
            # Build the classification prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(query, conversation_context)
            
            # Make API call to OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=1000
            )
            
            # Parse the response
            classification_result = self._parse_classification_response(
                response.choices[0].message.content,
                query
            )
            
            # Cache the result
            if use_cache:
                self._cache_result(query, classification_result)
            
            return classification_result
            
        except Exception as e:
            logger.error(f"Error during OpenAI classification: {str(e)}")
            return self._fallback_classification(query)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for classification."""
        return """You are an advanced query classifier for a restaurant management system. Your task is to analyze user queries and classify them into the appropriate category, extract relevant parameters, and assign a confidence score.

QUERY CATEGORIES:
- menu_inquiry: Questions about menu items, categories, availability, descriptions
- order_history: Requests for past order information, sales data, analytics
- price_update: Requests to modify item prices or costs
- pdf_ingestion: Document processing, file uploads, data extraction requests
- general: General questions that don't fit other categories

RESPONSE FORMAT:
You must respond with a valid JSON object containing:
{
    "query_type": "category_name",
    "confidence": 0.0-1.0,
    "parameters": {
        // Relevant extracted parameters based on query type
    },
    "needs_clarification": true/false,
    "reasoning": "Brief explanation of classification decision"
}

PARAMETER GUIDELINES:
- menu_inquiry: Extract item names, categories, attributes requested
- order_history: Extract time periods, filters, aggregation requests
- price_update: Extract item names and target prices
- pdf_ingestion: Extract file types, processing requirements
- general: Extract subject matter or topics

CONFIDENCE SCORING:
- 0.9-1.0: Very clear, unambiguous classification
- 0.7-0.8: Good classification with minor ambiguity
- 0.5-0.6: Moderate confidence, some uncertainty
- 0.3-0.4: Low confidence, significant ambiguity
- 0.0-0.2: Very uncertain, fallback classification

Always respond with valid JSON only."""

    def _build_user_prompt(self, query: str, conversation_context: Optional[Dict[str, Any]] = None) -> str:
        """Build the user prompt for classification."""
        prompt = f"Classify this query: \"{query}\""
        
        if conversation_context:
            prompt += f"\n\nConversation context: {json.dumps(conversation_context, indent=2)}"
        
        return prompt
    
    def _parse_classification_response(self, response_content: str, original_query: str) -> Dict[str, Any]:
        """Parse the OpenAI response into a classification result."""
        try:
            # Try to extract JSON from the response
            cleaned_response = response_content.strip()
            
            # Handle markdown code blocks
            if cleaned_response.startswith("```"):
                lines = cleaned_response.split("\n")
                cleaned_response = "\n".join(lines[1:-1])
            
            # Parse JSON
            result = json.loads(cleaned_response)
            
            # Validate required fields
            if "query_type" not in result:
                result["query_type"] = "general"
            if "confidence" not in result:
                result["confidence"] = 0.5
            if "parameters" not in result:
                result["parameters"] = {}
            if "needs_clarification" not in result:
                result["needs_clarification"] = False
            
            # Add original query
            result["query"] = original_query
            result["classification_method"] = "openai"
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response content: {response_content}")
            return self._fallback_classification(original_query)
        except Exception as e:
            logger.error(f"Error parsing classification response: {e}")
            return self._fallback_classification(original_query)
    
    def _fallback_classification(self, query: str) -> Dict[str, Any]:
        """Provide fallback classification using simple rules."""
        logger.warning(f"Using fallback classification for query: {query}")
        
        query_lower = query.lower()
        
        # Simple keyword-based classification
        if any(word in query_lower for word in ["order", "sales", "sold", "purchase", "history", "analytics"]):
            query_type = "order_history"
        elif any(word in query_lower for word in ["price", "cost", "update", "change"]):
            query_type = "price_update"
        elif any(word in query_lower for word in ["pdf", "document", "file", "upload", "import"]):
            query_type = "pdf_ingestion"
        elif any(word in query_lower for word in ["menu", "item", "dish", "food", "category"]):
            query_type = "menu_inquiry"
        else:
            query_type = "general"
        
        return {
            "query": query,
            "query_type": query_type,
            "confidence": 0.3,
            "parameters": {},
            "needs_clarification": True,
            "reasoning": "Fallback rule-based classification",
            "classification_method": "fallback"
        }
    
    def _check_cache(self, query: str) -> Optional[Dict[str, Any]]:
        """Check if query exists in cache."""
        normalized_query = query.lower().strip()
        return self._classification_cache.get(normalized_query)
    
    def _cache_result(self, query: str, result: Dict[str, Any]) -> None:
        """Cache classification result."""
        normalized_query = query.lower().strip()
        self._classification_cache[normalized_query] = result
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response."""
        return {
            "success": False,
            "error": error_message,
            "classification": self._fallback_classification(""),
            "routing": {
                "target_agent": "menu-qa-agent",
                "query_type": "general",
                "confidence": 0.1
            },
            "timestamp": time.time()
        }
    
    def get_supported_query_types(self) -> List[str]:
        """Get list of supported query types."""
        return list(self.agent_mapping.keys())
    
    def get_agent_mapping(self) -> Dict[str, str]:
        """Get the mapping of query types to agent names."""
        return self.agent_mapping.copy()
    
    def clear_cache(self) -> None:
        """Clear the classification cache."""
        self._classification_cache = {}
        logger.info("Classification cache cleared") 