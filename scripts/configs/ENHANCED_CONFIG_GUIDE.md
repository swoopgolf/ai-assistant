# Enhanced Agent Configuration Guide

This guide explains all the advanced configuration options you can add to agent configuration files to make them significantly more functional out of the box.

## 🔧 **Basic vs Enhanced Configurations**

### Basic Configuration (Original)
```json
{
  "agent_name": "my-agent",
  "description": "Basic agent description", 
  "port": 10200,
  "author_name": "Developer",
  "author_email": "dev@example.com",
  "capabilities": ["basic_task", "simple_processing"]
}
```

### Enhanced Configuration (New)
```json
{
  "agent_name": "my-agent",
  "description": "Comprehensive agent with detailed functionality",
  "port": 10200,
  "author_name": "Developer",
  "author_email": "dev@example.com", 
  "capabilities": ["advanced_task", "data_processing"],
  
  // 🚀 NEW: Detailed tool definitions
  "tools": [...],
  
  // 🚀 NEW: Database schema information
  "database_schema": {...},
  
  // 🚀 NEW: Dependencies and packages
  "dependencies": {...},
  
  // 🚀 NEW: Environment configuration
  "environment_variables": {...},
  
  // 🚀 NEW: Custom prompts and behavior
  "custom_prompts": {...},
  
  // 🚀 NEW: Security configuration
  "security_config": {...},
  
  // 🚀 NEW: Performance settings
  "performance_config": {...},
  
  // 🚀 NEW: Example interactions
  "example_interactions": [...]
}
```

## 📋 **Enhanced Configuration Sections**

### 1. **Tools Definition (`tools`)**
Define specific functions the agent can perform with detailed parameters.

```json
{
  "tools": [
    {
      "name": "tool_function_name",
      "description": "What this tool does",
      "parameters": {
        "param1": {
          "type": "string", 
          "description": "Parameter description",
          "required": true
        },
        "param2": {
          "type": "integer",
          "description": "Optional parameter",
          "required": false,
          "default": 10
        }
      },
      "returns": "Description of what the tool returns",
      "requires_confirmation": false
    }
  ]
}
```

**Benefits:**
- ✅ Auto-generates tool function signatures
- ✅ Provides parameter validation
- ✅ Documents expected inputs/outputs
- ✅ Enables type checking

### 2. **Database Schema (`database_schema`)**
Complete database structure information for data-aware agents.

```json
{
  "database_schema": {
    "tables": {
      "table_name": {
        "description": "What this table contains",
        "columns": {
          "column_name": {
            "type": "VARCHAR(255)",
            "description": "Column purpose",
            "constraints": ["NOT NULL", "UNIQUE"]
          }
        },
        "indexes": ["column1", "column2"]
      }
    },
    "sample_queries": [
      "SELECT * FROM table_name WHERE condition",
      "-- Query with comment explaining purpose"
    ]
  }
}
```

**Benefits:**
- ✅ Enables schema-aware SQL generation
- ✅ Provides query examples
- ✅ Documents database structure
- ✅ Helps with validation

### 3. **Dependencies (`dependencies`)**
Specify required Python packages and versions.

```json
{
  "dependencies": {
    "required": [
      "psycopg2-binary>=2.9.0",
      "sqlalchemy>=2.0.0", 
      "pydantic>=2.0.0"
    ],
    "optional": [
      "redis>=4.5.0",
      "matplotlib>=3.7.0"
    ]
  }
}
```

**Benefits:**
- ✅ Auto-installs required packages
- ✅ Ensures version compatibility
- ✅ Documents optional features
- ✅ Simplifies deployment

### 4. **Environment Variables (`environment_variables`)**
Define configuration variables and defaults.

```json
{
  "environment_variables": {
    "required": {
      "DB_HOST": {"description": "Database host", "default": "localhost"},
      "DB_PASSWORD": {"description": "Database password"}
    },
    "optional": {
      "CACHE_TTL": {"description": "Cache timeout", "default": "3600"},
      "LOG_LEVEL": {"description": "Logging level", "default": "INFO"}
    }
  }
}
```

**Benefits:**
- ✅ Documents configuration requirements
- ✅ Provides sensible defaults
- ✅ Enables environment-specific settings
- ✅ Improves deployment flexibility

### 5. **Custom Prompts (`custom_prompts`)**
Tailored prompts for specific agent behavior.

```json
{
  "custom_prompts": {
    "system_prompt": "You are a specialized agent that...",
    "tool_selection_prompt": "Choose tools based on...",
    "error_handling": "When errors occur, do...",
    "validation_prompt": "Validate inputs by..."
  }
}
```

**Benefits:**
- ✅ Defines agent personality and behavior
- ✅ Provides context-specific guidance
- ✅ Improves response quality
- ✅ Ensures consistent behavior

### 6. **Security Configuration (`security_config`)**
Security settings and access controls.

```json
{
  "security_config": {
    "database_access": "read_only",
    "allowed_operations": ["SELECT"],
    "rate_limiting": {
      "requests_per_minute": 100,
      "burst_allowance": 20
    },
    "input_validation": {
      "max_query_length": 500,
      "blocked_patterns": ["DROP", "DELETE"]
    }
  }
}
```

**Benefits:**
- ✅ Enforces security policies
- ✅ Prevents unauthorized operations
- ✅ Controls access levels
- ✅ Implements rate limiting

### 7. **Performance Configuration (`performance_config`)**
Optimization and caching settings.

```json
{
  "performance_config": {
    "caching": {
      "enabled": true,
      "cache_ttl_seconds": 300,
      "cache_key_prefix": "agent_cache"
    },
    "query_optimization": {
      "use_indexes": true,
      "max_results_per_query": 50,
      "query_timeout_seconds": 10
    }
  }
}
```

**Benefits:**
- ✅ Improves response times
- ✅ Reduces database load
- ✅ Configures timeouts
- ✅ Optimizes resource usage

### 8. **Example Interactions (`example_interactions`)**
Sample conversations and expected behavior.

```json
{
  "example_interactions": [
    {
      "user_input": "What's the price of a burger?",
      "expected_tool": "get_item_price",
      "expected_params": {"item_name": "burger"},
      "sample_response": "The burger is $12.95..."
    }
  ]
}
```

**Benefits:**
- ✅ Provides usage examples
- ✅ Documents expected behavior
- ✅ Helps with testing
- ✅ Guides implementation

## 🎯 **Agent-Specific Enhanced Examples**

### Menu Q&A Agent Enhanced Features
- **7 specialized tools** (get_menu_item, search_by_category, etc.)
- **Complete menu database schema** with allergens and dietary flags
- **Custom prompts** for menu assistance
- **Read-only security** configuration
- **Caching** for performance

### Order History Analytics Agent Enhanced Features  
- **7 analytics tools** (sales_summary, top_selling_items, etc.)
- **Comprehensive order/customer schema** with relationships
- **Business intelligence prompts** with insight generation
- **Data masking** for sensitive information
- **Query optimization** settings

### Price Update Agent Enhanced Features
- **7 update tools** with validation and confirmation
- **Audit logging** schema for change tracking
- **Approval workflows** and change limits
- **Confirmation prompts** for safety
- **Validation rules** for business logic

### PDF Ingestion Agent Enhanced Features
- **8 document processing tools** with OCR support
- **File validation** and security checks
- **Import logging** and reporting
- **Extraction configuration** with parsing rules
- **Memory management** for large files

## 🚀 **Using Enhanced Configurations**

### Create Enhanced Agents
```bash
# Use enhanced configs (recommended)
python scripts/create_new_agent.py --config scripts/configs/menu-qa-agent-enhanced.json

# Or create all enhanced agents at once
python scripts/create_club_management_agents.py --enhanced
```

### What Gets Generated
When using enhanced configurations, the creation script generates:

1. **More sophisticated tool implementations**
2. **Database connection code with schema awareness**
3. **Environment variable handling**
4. **Custom prompt integration**
5. **Security validation functions**
6. **Performance optimization features**
7. **Comprehensive error handling**

## 📈 **Benefits of Enhanced Configurations**

| Feature | Basic Config | Enhanced Config |
|---------|-------------|------------------|
| **Setup Time** | Manual implementation needed | Ready to customize |
| **Documentation** | Minimal | Comprehensive |
| **Security** | Basic | Production-ready |
| **Performance** | No optimization | Built-in caching/optimization |
| **Validation** | Manual | Automatic |
| **Examples** | None | Complete interaction examples |
| **Dependencies** | Manual install | Auto-managed |

## 💡 **Best Practices**

### 1. **Always Use Enhanced Configs for Production**
Enhanced configurations provide production-ready features that basic configs lack.

### 2. **Customize Prompts for Your Domain**
Tailor the `custom_prompts` section to match your specific business requirements.

### 3. **Define Complete Database Schemas**
Include all tables, columns, relationships, and sample queries your agent needs.

### 4. **Implement Proper Security**
Use appropriate access levels, rate limiting, and validation for your use case.

### 5. **Provide Realistic Examples**
Include diverse example interactions that cover your agent's main use cases.

### 6. **Version Dependencies Carefully**
Pin specific package versions to ensure compatibility and reproducibility.

## 🔧 **Customization Guide**

### Modify Existing Enhanced Configs
```bash
# Copy an enhanced config as a starting point
cp scripts/configs/menu-qa-agent-enhanced.json scripts/configs/my-custom-agent.json

# Edit the configuration
# - Change agent_name, port, description
# - Modify tools for your specific needs
# - Update database_schema for your tables
# - Customize prompts for your domain
# - Adjust security and performance settings

# Create your custom agent
python scripts/create_new_agent.py --config scripts/configs/my-custom-agent.json
```

### Add New Tool Definitions
```json
{
  "tools": [
    {
      "name": "my_custom_tool",
      "description": "Performs custom business logic",
      "parameters": {
        "input_data": {"type": "object", "description": "Input parameters"},
        "options": {"type": "array", "description": "Processing options", "required": false}
      },
      "returns": "Processed results with metadata"
    }
  ]
}
```

## 📚 **Available Enhanced Configurations**

All enhanced configurations are in `scripts/configs/`:

- `menu-qa-agent-enhanced.json` - Menu queries and information
- `order-history-qa-agent-enhanced.json` - Sales analytics and BI
- `price-update-agent-enhanced.json` - Menu editing and updates  
- `pdf-ingestion-agent-enhanced.json` - Document processing

Each includes 100+ configuration options across all sections for maximum functionality out of the box.

---

*Enhanced configurations transform basic agent templates into production-ready, domain-specific agents with minimal additional development required.* 