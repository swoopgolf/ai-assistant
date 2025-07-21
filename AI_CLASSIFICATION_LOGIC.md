# AI-Powered Query Classification Logic in Swoop AI

This document summarizes the core logic for AI-powered query classification within the `old-code/swoop-ai/services/classification` directory.

## 1. `QueryClassifierInterface` (`classifier_interface.py`)

This file serves as the public-facing interface for the classification service.

-   **Initialization:** It initializes instances of `ClassificationService` (the main AI classifier) and `ClassificationPromptBuilder` (used for constructing prompts for the AI model).
-   **Database Schema:** It loads a predefined database schema and passes it to both the `ClassificationService` and `ClassificationPromptBuilder` to provide essential context for accurate query classification.
-   **`classify_query` Method:** This is the primary entry point for classifying user queries. It delegates the actual classification task to the underlying `ClassificationService.classify_query` or `get_classification_with_context` methods.
-   **Error Handling:** Includes robust error logging and returns a fallback classification result if any errors occur during the process.
-   **Utility Methods:** Provides methods to retrieve supported query types and clear the classification cache.

## 2. `ClassificationService` (`classifier.py`)

This file contains the core AI-powered classification logic, primarily leveraging the OpenAI API.

-   **Initialization:** Sets up an OpenAI client (defaulting to `gpt-4o-mini`) and securely retrieves API keys from configuration or environment variables.
-   **Prompt Construction:** Utilizes the `ClassificationPromptBuilder` to dynamically create system and user prompts, which are then sent to the OpenAI API for classification.
-   **`classify_query` Method Details:**
    -   **Caching:** Implements a local cache to store and retrieve results for previously classified queries, improving efficiency.
    -   **Mock Responses:** Includes specific mock responses for certain test queries to facilitate testing.
    -   **OpenAI API Call:** Constructs detailed prompts (including conversation context like session history when available) and sends them to the OpenAI `chat.completions.create` endpoint.
    -   **Response Parsing:** Parses the JSON response received from the OpenAI API, extracting key information such as `query_type`, `confidence`, and `parameters`. It handles various JSON formats, including those embedded within markdown code blocks.
    -   **Parameter Validation:** Validates the extracted parameters and adjusts the confidence score accordingly. If critical parameters are missing, it sets a `needs_clarification` flag.
    -   **Caching Results:** Stores the classification result in the cache for future use.
-   **`get_classification_with_context`:** Enhances classification accuracy by leveraging conversation context to resolve ambiguities, fill in missing parameters (e.g., time periods, entities), or identify follow-up questions.
-   **`_fallback_classification`:** Provides a rule-based fallback classification mechanism in cases where the AI service encounters errors or fails to provide a valid response.
-   **`check_if_followup`:** Makes a dedicated LLM call to determine if a new query is a direct follow-up to the previous turn, using pronouns and contextual phrases as indicators.

## 3. `QueryClassifier` (`query_classifier.py`)

This file appears to implement an older or complementary rule-based classification system, distinct from the AI-powered approach in `classifier.py`. It likely serves as a fallback or a simpler initial classification layer.

-   **Keyword-Based Classification:** Defines extensive keyword lists for different query types: `order_history`, `menu`, `action`, `clarification`, and `correction`.
-   **`classify` Method Details:**
    -   **Correction Detection:** First checks if the incoming query is a "correction" to a previous interaction.
    -   **Rule-Based Classification:** Employs `_rule_based_classification` which uses keyword matching and basic linguistic rules (e.g., presence of question marks) to determine the query type and assign a confidence score.
    -   **Parameter Extraction:** Extracts parameters relevant to the identified query type using helper methods like `_extract_order_history_params`, `_extract_menu_params`, etc. These methods also rely on rule-based approaches, such as regular expressions for identifying dates, prices, and entities.
    -   **Clarification:** Determines if further clarification is needed based on missing or ambiguous parameters and generates appropriate clarification questions.

## Conclusion

The primary AI-powered query classification in Swoop AI is handled by `old-code/swoop-ai/services/classification/classifier.py`, which integrates with the OpenAI API. `classifier_interface.py` provides a clean abstraction layer, while `query_classifier.py` offers a supplementary rule-based classification system. 