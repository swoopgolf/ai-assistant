# 🤖 Multi-Agent Framework

[![Framework Version](https://img.shields.io/badge/Version-2.0.0-blue.svg)](https://github.com/your-repo/multi-agent-framework)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/Docs-Available-green.svg)](docs/)

> **A reusable, scalable multi-agent framework with A2A (Agent-to-Agent) communication protocol for building distributed agent systems.**

## 🌟 **Framework Overview**

This Multi-Agent Framework provides a robust foundation for building distributed systems where specialized agents collaborate to accomplish complex tasks. The framework includes an orchestrator for coordination, common utilities for shared functionality, and a template system for easily creating new agents.

### **🎯 Key Features**

- 🤖 **Agent-to-Agent Communication**: JSON-RPC based inter-agent communication via hub-and-spoke architecture
- 🏗️ **Modular Architecture**: Clean separation between orchestrator, agents, and common utilities
- 📦 **Agent Template**: Pre-built template for quickly creating new specialized agents
- 🔐 **Enterprise Security**: Built-in authentication, authorization, and audit logging
- 📊 **Observability**: OpenTelemetry tracing, Prometheus metrics, health monitoring
- 🐳 **Container Ready**: Docker and Docker Compose support for easy deployment
- ⚡ **MCP Tool Server**: Model Context Protocol support for external tool integration
- 🔧 **Configuration Management**: Centralized YAML-based configuration system

### **🏗️ Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                          │
│                 (Central Coordinator)                          │
│                    Port: 10005                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │ A2A Communication (JSON-RPC)
                      │ Hub-and-Spoke Model
         ┌────────────┼────────────┐
         │            │            │
    ┌────▼───┐   ┌───▼────┐   ┌───▼────┐
    │ Agent  │   │ Agent  │   │  MCP   │
    │Template│   │   X    │   │ Tool   │
    │ :10100 │   │ :Port  │   │Server  │
    └────────┘   └────────┘   │ :11000 │
                              └────────┘
```

## 🚀 **Quick Start**

### **Prerequisites**

- Python 3.11+
- Docker (optional, for containerized deployment)

### **1. Clone and Setup**

```bash
git clone <repository-url>
cd multi-agent-framework
pip install -r requirements.txt
```

### **2. Start Core Framework**

```bash
# Option 1: Using PowerShell script (Windows)
./start_all_agents_simple.ps1

# Option 2: Manual startup
cd orchestrator-agent && python -m orchestrator_agent &
cd agent_template && python -m agent_template &
```

### **3. Verify Framework**

```bash
# Check orchestrator health
curl http://localhost:10005/health

# Check agent template health
curl http://localhost:10100/health
```

### **4. Using Docker Compose**

```bash
docker-compose up -d
```

## 🔧 **Creating Your First Agent**

### **Step 1: Copy Template**

```bash
cp -r agent_template my-custom-agent
cd my-custom-agent
```

### **Step 2: Customize Agent**

1. **Rename package**: `mv agent_template my_agent`
2. **Update `pyproject.toml`**: Change name, description, dependencies
3. **Edit `__main__.py`**: Update agent name, port, and description
4. **Implement logic in `agent_executor.py`**: Add your specific functionality
5. **Define tools in `tools.py`**: Create tools your agent exposes
6. **Customize `prompt.py`**: Set agent behavior and instructions

### **Step 3: Register Agent**

Add your agent to `config/system_config.yaml`:

```yaml
agents:
  my_custom_agent:
    host: "localhost"
    port: 10101
    description: "My custom agent description"
    capabilities:
      - "my_custom_skill"
```

### **Step 4: Test Agent**

```bash
cd my-custom-agent
python -m my_agent
```

📖 **For detailed instructions, see [docs/adding_agents.md](docs/adding_agents.md)**

## 📁 **Project Structure**

```
multi-agent-framework/
├── agent_template/              # Template for creating new agents
├── common_utils/               # Shared utilities and libraries
│   ├── mcp_server/            # MCP tool server implementation
│   ├── agent_config.py        # Agent configuration management
│   ├── security.py            # Security utilities
│   └── ...                    # Other shared modules
├── config/                    # Configuration files
│   └── system_config.yaml     # Main system configuration
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md        # System architecture overview
│   └── adding_agents.md       # Guide for creating agents
├── orchestrator-agent/        # Central orchestrator
├── monitoring/               # Observability configuration
├── scripts/                  # Utility scripts
├── tests/                    # Test suites
├── docker-compose.yml        # Container orchestration
└── README.md                 # This file
```

## 🛠️ **Core Components**

### **Orchestrator Agent**

The central hub that coordinates all agent communication:
- Routes tasks between agents
- Manages workflow execution
- Provides centralized logging and monitoring
- Handles service discovery

### **Agent Template**

A complete template for creating new agents:
- Pre-configured project structure
- Example tools and skills implementation
- Integration with common utilities
- Health monitoring and error handling

### **Common Utilities**

Shared libraries providing:
- Configuration management
- Security and authentication
- Logging and observability
- Data handle management
- Circuit breaker patterns

### **MCP Tool Server**

Model Context Protocol server for:
- Exposing agent tools to external systems
- Remote procedure call handling
- Tool discovery and documentation

## 📊 **Monitoring & Observability**

The framework includes comprehensive monitoring:

- **Prometheus**: Metrics collection on port 9090
- **Grafana**: Visualization dashboard on port 3000
- **OpenTelemetry**: Distributed tracing
- **Health Endpoints**: `/health` on each agent

Access monitoring:
```bash
# Prometheus metrics
http://localhost:9090

# Grafana dashboard (admin/admin123)
http://localhost:3000
```

## 🔒 **Security Features**

- **API Key Authentication**: Secure agent-to-agent communication
- **Rate Limiting**: Protection against abuse
- **CORS Configuration**: Cross-origin request handling
- **Security Headers**: HSTS, CSP, and other security headers
- **Audit Logging**: Comprehensive audit trails

## 🚢 **Deployment**

### **Docker Deployment**

```bash
# Build and start all services
docker-compose up -d

# Scale agents
docker-compose up -d --scale agent-template=3
```

### **Production Considerations**

- Use environment variables for sensitive configuration
- Enable monitoring alerts
- Configure proper log rotation
- Set up load balancing for high availability
- Use secrets management for API keys

## 🧪 **Testing**

```bash
# Run unit tests
pytest tests/

# Run integration tests
python tests/run_integration_tests.py

# Test specific agent
pytest tests/integration/test_a2a_communication.py
```

## 📚 **Documentation**

- [Architecture Overview](docs/ARCHITECTURE.md) - System design and communication flow
- [Adding Agents Guide](docs/adding_agents.md) - Step-by-step agent creation
- [API Documentation](docs/api/) - REST API specifications

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Follow the agent template structure for consistency
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📝 **License**

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Documentation**: Check the `docs/` directory
- **Issues**: Report bugs via GitHub Issues
- **Examples**: See `agent_template/` for implementation examples

## 🔮 **Roadmap**

- [ ] Kubernetes deployment manifests
- [ ] Agent auto-discovery and registration
- [ ] WebSocket support for real-time communication
- [ ] Plugin system for external integrations
- [ ] Enhanced security with mutual TLS
- [ ] Performance optimization and caching 