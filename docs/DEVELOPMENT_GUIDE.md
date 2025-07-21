# Club Management Agent System - Development Guide

This guide outlines the complete implementation plan for the club management agent system with four specialized agents for restaurant/club operations.

## System Overview

The system consists of:
- **Orchestrator Agent** (Port 10200) - Central coordination and task delegation
- **Order History QA Agent** (Port 10210) - Sales analytics and business intelligence ✅ COMPLETED
- **Menu QA Agent** (Port 10220) - Menu queries and information lookup ✅ COMPLETED
- **Price Update Agent** (Port 10410) - Menu editing and price modifications 🔄 IN PROGRESS
- **PDF Ingestion Agent** (Port 10350) - Document processing and item extraction

## Quick Start

### 1. Environment Setup

1. Copy the environment template:
   ```bash
   cp config/environment.env .env
   ```

2. Update database credentials in `.env`:
   ```bash
   DB_USER=your_actual_username
   DB_PASSWORD=your_actual_password
   ```

3. Install dependencies for each agent:
   ```bash
   cd order-history-qa-agent && pip install -e .
   cd ../menu-qa-agent && pip install -e .
   cd ../price-update-agent && pip install -e .
   cd ../pdf-ingestion-agent && pip install -e .
   ```

### 2. Database Setup

The system uses PostgreSQL with existing tables from `database.csv`:
- `orders` - Main orders table
- `order_items` - Individual items within orders  
- `users` - Customer information
- `items` - Menu items and pricing
- `categories` - Menu categories
- `menus` - Menu organization

## Implementation Tasks

### ✅ Completed Agents
- **Order History QA Agent** - All tools and business logic implemented
- **Menu QA Agent** - All tools and business logic implemented  
- **Price Update Agent Tools** - All 7 tools implemented (requires table creation)

### ✅ All Core Tasks Completed!

#### 1. Database Tables ✅ COMPLETED
All required tables have been created and verified:

```sql
-- price_history table (required for Price Update Agent audit logging)
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES items(id),
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2),
    change_reason TEXT,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- import_log table (required for PDF Ingestion Agent)
CREATE TABLE import_log (
    id SERIAL PRIMARY KEY,
    document_name VARCHAR(255),
    document_path TEXT,
    items_found INTEGER,
    items_imported INTEGER,
    items_skipped INTEGER,
    items_failed INTEGER,
    import_status VARCHAR(50),
    error_details JSON,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location_id INTEGER
);

-- promotional_pricing table (optional for enhanced price management)
CREATE TABLE promotional_pricing (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES items(id),
    promo_price DECIMAL(10,2),
    start_date DATE,
    end_date DATE,
    promo_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true
);

-- Create indexes for performance
CREATE INDEX idx_price_history_item_id ON price_history(item_id);
CREATE INDEX idx_import_log_status ON import_log(import_status);
CREATE INDEX idx_promotional_pricing_active ON promotional_pricing(is_active);
```

#### 2. Price Update Agent Business Logic ✅ COMPLETED
File: `price-update-agent/price_update_agent/agent_executor.py`
- ✅ Implement price change workflows with task routing
- ✅ Add approval process logic for large changes
- ✅ Configure audit logging integration
- ✅ Add validation rules and caching

#### 3. Implement PDF Ingestion Agent
**Tools** (`pdf-ingestion-agent/pdf_ingestion_agent/tools.py`):
- [x] `extract_menu_from_pdf` - Structured extraction using Google Gemini
- [x] `validate_extracted_items` - Data validation and cleaning
- [x] `categorize_items` - Automatic item categorization
- [x] `insert_menu_items` - Database insertion into `items` table
- [x] `generate_import_report` - Import process reporting

**Business Logic** (`pdf-ingestion-agent/pdf_ingestion_agent/agent_executor.py`):
- [x] Implement PDF processing workflows
- [x] Configure batch processing
- [x] Add error handling and retry logic

#### 4. Install Required Dependencies ✅ COMPLETED

**All Dependencies Installed:**
- ✅ redis>=4.5.0 (Price Update Agent)
- ✅ google-generativeai>=0.8.0 (PDF Ingestion Agent)  
- ✅ fuzzywuzzy>=0.18.0 python-levenshtein>=0.21.0 (Menu QA Agent)
- ✅ PyJWT, aiofiles, pydantic-settings (Framework dependencies)

#### 5. Testing Framework ✅ READY
- ✅ Agent health check testing script created (`test_agents.py`)
- ✅ Configuration validation implemented
- ✅ Individual agent startup testing
- ✅ System status monitoring

### Development Status Summary

All core development tasks have been completed:

1. ✅ **Database tables created** - All required tables exist and validated
2. ✅ **Price Update Agent completed** - Full business logic implemented
3. ✅ **PDF Ingestion Agent completed** - All tools and business logic ready
4. ✅ **Dependencies installed** - All required packages available
5. ✅ **Testing framework ready** - Comprehensive test script available

**🎯 System is ready for production deployment and testing!**

## Testing the System

### Quick System Test
Run the comprehensive test script to validate your setup:

```bash
python test_agents.py
```

This script will:
- ✅ Check environment configuration
- ✅ Test database connectivity  
- ✅ Validate all agent health endpoints
- ✅ Attempt startup testing if no agents running
- ✅ Provide system status summary

### Manual Testing Steps

1. **Test Configuration**:
```bash
   python -c "from common_utils.config import settings; print('✅ Config OK')"
```

2. **Test Database Connection**:
```bash
   cd scripts && python check_table_structure.py
   ```

3. **Test Individual Agent**:
   ```bash
   cd menu-qa-agent
   python -m menu_qa_agent &
   curl http://localhost:10220/health
   ```

## Running the System

### Start Individual Agents
```bash
# Terminal 1 - Order History QA Agent
cd order-history-qa-agent
python -m order_history_qa_agent

# Terminal 2 - Menu QA Agent  
cd menu-qa-agent
python -m menu_qa_agent

# Terminal 3 - Price Update Agent
cd price-update-agent
python -m price_update_agent

# Terminal 4 - PDF Ingestion Agent
cd pdf-ingestion-agent
python -m pdf_ingestion_agent

# Terminal 5 - Orchestrator Agent
cd orchestrator-agent
python -m orchestrator_agent
```

### Using Docker Compose
```bash
docker-compose up -d
```

## Example Usage

### Order Analytics ✅ WORKING
```
User: "What were our total sales last week?"
Orchestrator → Order History QA Agent → get_sales_summary
Response: "Last week we had $12,450 in sales across 187 orders..."
```

### Menu Queries ✅ WORKING
```
User: "What vegetarian options do we have?"
Orchestrator → Menu QA Agent → search_by_dietary_restriction
Response: "We have 8 vegetarian options including Garden Salad ($12)..."
```

### Price Updates 🔄 NEEDS DATABASE TABLES
```
User: "Increase Caesar Salad price to $15"
Orchestrator → Price Update Agent → update_item_price
Response: "Updated Caesar Salad from $13.95 to $15.00 (7.5% increase)..."
```

### Document Processing ✅ COMPLETED
```
User: "Process this PDF menu and add the items"
Orchestrator → PDF Ingestion Agent → extract_menu_from_pdf → validate_extracted_items → categorize_items → insert_menu_items → generate_import_report
Response: "Processed 23 items from PDF, successfully imported 21 items..."
```

## Troubleshooting

### Common Issues
1. **Database Connection Errors**: Check credentials in `.env`
2. **Port Conflicts**: Ensure ports 10200, 10210, 10220, 10350, 10410 are available
3. **Missing Dependencies**: Run `pip install -e .` in each agent directory
4. **Permission Errors**: Ensure database user has required permissions

### Debugging
- Set `LOG_LEVEL=DEBUG` in environment
- Check agent logs in their respective directories
- Use health endpoints to verify agent status
- Test database connectivity with `test_connection()` function 