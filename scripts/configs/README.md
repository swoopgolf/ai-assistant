# Club Management Agent Configurations

This directory contains configuration files for creating specialized agents that form a complete club management system. These agents implement the architecture described in the main project documentation and follow the A2A (Agent-to-Agent) protocol for multi-agent coordination.

## 🏗️ System Architecture

The club management system follows a **hub-and-spoke model** with the orchestrator acting as the central coordinator that delegates tasks to specialized agents:

```
User Request → Orchestrator → Appropriate Specialist Agent → Database/Action → Response
```

### Core Principles (from ARCHITECTURE.md)

- **Opaque Execution**: Each agent's internal workings are a black box to the orchestrator
- **Hub-and-Spoke Model**: All communication is mediated by the orchestrator
- **Asynchronous Operations**: All interactions are non-blocking to support long-running tasks
- **Clear Separation**: Agents are problem-solving collaborators, tools are for executing well-defined actions

## 🤖 Available Agents

### 1. Order History Q&A Agent (`order-history-qa-agent.json`)
- **Port**: 10210 (Data Processing Range)
- **Purpose**: Business intelligence and sales analytics
- **Data Source**: Cloud SQL PostgreSQL (byrdi database)
- **Core Function**: Natural language to SQL conversion for order history queries

**Example Interactions:**
- "What were last month's total sales?"
- "What's our best-selling item on weekends?"
- "Show me revenue trends for the past quarter"
- "How many orders were placed yesterday?"

**Capabilities:**
- `sales_analytics` - Generate sales reports and insights
- `order_history_queries` - Query historical order data
- `natural_language_to_sql` - Convert questions to SQL queries
- `business_intelligence` - Provide strategic insights
- `revenue_reporting` - Financial analysis and reporting
- `customer_analytics` - Customer behavior analysis
- `trend_analysis` - Identify patterns and trends
- `performance_metrics` - KPI tracking and measurement

### 2. Menu Q&A Agent (`menu-qa-agent.json`)
- **Port**: 10220 (Data Processing Range)  
- **Purpose**: Menu information and item lookup
- **Data Source**: Menu items table in PostgreSQL
- **Core Function**: Menu queries and information retrieval

**Example Interactions:**
- "What sandwiches do we offer at the clubhouse?"
- "Is the vegan burger gluten-free?"
- "How much does a pint of IPA cost?"
- "Do we have any gluten-free beer options?"

**Capabilities:**
- `menu_queries` - Answer questions about menu items
- `item_lookup` - Find specific items and details
- `price_inquiry` - Provide current pricing information
- `availability_check` - Check item availability status
- `dietary_information` - Dietary restrictions and allergen info
- `ingredient_search` - Search by ingredients or components
- `category_browsing` - Browse items by category
- `menu_navigation` - Help users navigate menu options

### 3. Price Update Agent (`price-update-agent.json`)
- **Port**: 10410 (Communication/Action Range)
- **Purpose**: Menu editing and price modifications
- **Data Source**: Menu items table (write operations)
- **Core Function**: Execute database updates via natural language commands

**Example Interactions:**
- "Increase the price of the Caesar Salad to $12"
- "Set all appetizers $2 cheaper during happy hour"
- "Raise all egg dishes by 10%"
- "Mark the fish and chips as out of stock"

**Capabilities:**
- `price_updates` - Modify individual item prices
- `menu_editing` - Edit item details and descriptions
- `item_modifications` - Update item attributes
- `availability_management` - Control item availability
- `bulk_price_changes` - Update multiple items at once
- `category_adjustments` - Modify entire categories
- `promotional_pricing` - Set special pricing
- `audit_logging` - Track all changes for compliance
- `change_validation` - Ensure updates are valid and safe

### 4. PDF Ingestion Agent (`pdf-ingestion-agent.json`)
- **Port**: 10350 (File Handling Range)
- **Purpose**: Document processing and menu item extraction  
- **Data Source**: PDF documents (supplier menus, corporate updates)
- **Core Function**: Extract structured data from unstructured documents

**Example Interactions:**
- "Here's a PDF of our new summer menu, please add these items"
- "Import the beverage list from this supplier document"
- "Extract menu items from this catering menu PDF"

**Capabilities:**
- `pdf_text_extraction` - Extract text from PDF documents
- `ocr_processing` - Handle scanned/image-based PDFs
- `menu_item_parsing` - Identify and structure menu items
- `structured_data_extraction` - Convert unstructured text to data
- `document_analysis` - Analyze document format and layout
- `data_validation` - Ensure extracted data is valid
- `bulk_item_insertion` - Insert multiple items efficiently
- `format_detection` - Identify document format patterns
- `import_reporting` - Report on import success/failures

## 🚀 Quick Start

### Create All Agents at Once

```bash
python scripts/create_club_management_agents.py
```

### Create Individual Agents

```bash
# Create just the order history agent
python scripts/create_club_management_agents.py --agent order-history

# Create just the menu Q&A agent  
python scripts/create_club_management_agents.py --agent menu-qa

# Create just the price update agent
python scripts/create_club_management_agents.py --agent price-update

# Create just the PDF ingestion agent
python scripts/create_club_management_agents.py --agent pdf-ingestion
```

### Manual Creation

```bash
# Using individual config files
python scripts/create_new_agent.py --config scripts/configs/order-history-qa-agent.json
python scripts/create_new_agent.py --config scripts/configs/menu-qa-agent.json
python scripts/create_new_agent.py --config scripts/configs/price-update-agent.json
python scripts/create_new_agent.py --config scripts/configs/pdf-ingestion-agent.json
```

## 🔧 Implementation Requirements

After creating the agents, you'll need to implement specific functionality:

### 1. Database Connectivity
All agents need connection to Cloud SQL PostgreSQL:
- **Host**: `34.83.218.41` (public IP)
- **Port**: `5432`
- **Database**: `byrdi`
- **Security**: Use service accounts or IAM authentication

### 2. Schema Knowledge
Agents need awareness of database schema:
- `orders` table - Order records with dates, totals, customer info
- `order_items` table - Individual items within orders
- `menu_items` table - Current menu with prices, descriptions, categories
- Additional tables as needed for your specific implementation

### 3. Security Considerations
- **Read-only access** for Order History and Menu Q&A agents
- **Write access** only for Price Update and PDF Ingestion agents
- **Input validation** to prevent SQL injection
- **Audit logging** for all database modifications
- **Error handling** for invalid queries or operations

### 4. LLM Integration
- **Natural Language Processing** for intent recognition
- **SQL Generation** from natural language queries
- **Response Formatting** for user-friendly output
- **Context Management** for multi-turn conversations

## 🔌 Integration with Orchestrator

The orchestrator should implement intent recognition to route requests:

```python
def route_request(user_input: str) -> str:
    """Route user request to appropriate agent."""
    
    # Analytics keywords
    if any(word in user_input.lower() for word in ['sales', 'revenue', 'orders', 'analytics', 'report']):
        return 'order_history_qa_agent'
    
    # Menu inquiry keywords  
    elif any(word in user_input.lower() for word in ['menu', 'item', 'price', 'available', 'offer']):
        return 'menu_qa_agent'
    
    # Update/modification keywords
    elif any(word in user_input.lower() for word in ['update', 'change', 'set', 'increase', 'decrease']):
        return 'price_update_agent'
    
    # PDF/document keywords
    elif any(word in user_input.lower() for word in ['pdf', 'import', 'add items', 'extract']):
        return 'pdf_ingestion_agent'
    
    else:
        return 'default_handler'
```

## 📊 Port Allocation

The agents use ports in designated ranges:

- **10210**: Order History Q&A (Data Processing)
- **10220**: Menu Q&A (Data Processing)  
- **10350**: PDF Ingestion (File Handling)
- **10410**: Price Update (Communication/Action)

These follow the port allocation strategy documented in the main README.

## 🧪 Testing Strategy

1. **Individual Agent Testing**
   ```bash
   # Test each agent independently
   curl http://localhost:10210/health  # Order History
   curl http://localhost:10220/health  # Menu Q&A
   curl http://localhost:10350/health  # PDF Ingestion  
   curl http://localhost:10410/health  # Price Update
   ```

2. **Integration Testing**
   - Test orchestrator routing to each agent
   - Verify database connectivity and operations
   - Test multi-turn conversations
   - Validate security and error handling

3. **End-to-End Testing**
   - Complete workflows from user input to final response
   - Test with real data and realistic queries
   - Performance testing under load

## 🚀 Deployment to Vertex AI

Once implemented and tested, deploy to Vertex AI for production:

1. **Containerize Agents**
   - Build Docker containers for each agent
   - Include all dependencies and database drivers

2. **Vertex AI Integration**
   - Use Vertex AI Agent Builder for conversational UI
   - Deploy agents on Cloud Run or GKE
   - Configure secure database connections

3. **Monitoring and Logging**
   - Set up Cloud Monitoring for agent health
   - Configure logging for all database operations
   - Implement tracing for request routing

## 📚 Related Documentation

- [Main Architecture](../../docs/ARCHITECTURE.md) - System design principles
- [Adding Agents Guide](../../docs/adding_agents.md) - Detailed agent creation process
- [Agent Creation Scripts](../README.md) - Script documentation and usage

---

*This configuration supports the vision of a conversational AI assistant for club management, enabling managers to interact with their data and systems through natural language, similar to Avocado's AI assistant functionality.* 