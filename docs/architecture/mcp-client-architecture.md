# VeoGen MCP Client Architecture

## Overview
VeoGen functions as a sophisticated MCP (Model Context Protocol) client, enabling AI chat partners to perform real-world actions through integrated MCP servers. This architecture transforms conversations into executable workflows across multiple domains.

## Core MCP Client Configuration

### Client Setup Architecture
```python
# backend/app/services/mcp_client_service.py
import asyncio
from typing import Dict, List, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClientManager:
    def __init__(self):
        self.active_sessions: Dict[str, ClientSession] = {}
        self.available_mcps = {
            "blender": {
                "command": "node",
                "args": ["./mcp-servers/blender-mcp/dist/index.js"],
                "capabilities": ["3d_modeling", "rendering", "animation"]
            },
            "everart": {
                "command": "node", 
                "args": ["./mcp-servers/everart-mcp/dist/index.js"],
                "capabilities": ["image_generation", "style_transfer"]
            },
            "puppeteer": {
                "command": "node",
                "args": ["./mcp-servers/puppeteer-mcp/dist/index.js"], 
                "capabilities": ["web_automation", "scraping", "testing"]
            },
            "postgres": {
                "command": "node",
                "args": ["./mcp-servers/postgres-mcp/dist/index.js"],
                "capabilities": ["database_queries", "analytics"]
            },
            "memory": {
                "command": "node",
                "args": ["./mcp-servers/memory-mcp/dist/index.js"],
                "capabilities": ["knowledge_graphs", "entity_management"]
            }
        }
    
    async def initialize_mcp(self, mcp_name: str) -> ClientSession:
        """Initialize and connect to an MCP server"""
        if mcp_name in self.active_sessions:
            return self.active_sessions[mcp_name]
        
        config = self.available_mcps[mcp_name]
        server_params = StdioServerParameters(
            command=config["command"],
            args=config["args"]
        )
        
        session = await stdio_client(server_params)
        await session.initialize()
        
        self.active_sessions[mcp_name] = session
        return session
    
    async def execute_mcp_tool(self, mcp_name: str, tool_name: str, arguments: Dict[str, Any]):
        """Execute a tool through the specified MCP"""
        session = await self.initialize_mcp(mcp_name)
        result = await session.call_tool(tool_name, arguments)
        return result
```

## Available MCP Integrations

### 1. Blender MCP - 3D Content Creation
**Capabilities:**
- Create 3D models from text descriptions
- Generate architectural visualizations
- Animate objects and scenes
- Export models for 3D printing
- Render photorealistic images

**Example Usage:**
```python
# Create a modern chair
result = await mcp_client.execute_mcp_tool("blender", "create_model", {
    "prompt": "modern ergonomic office chair with mesh back",
    "style": "contemporary",
    "export_format": "stl"
})
```

### 2. EverArt MCP - Image Generation
**Capabilities:**
- Generate images from text prompts
- Style transfer and artistic effects
- Multiple AI models (FLUX, Stable Diffusion, Recraft)
- High-resolution outputs

**Example Usage:**
```python
# Generate concept art
result = await mcp_client.execute_mcp_tool("everart", "generate_image", {
    "prompt": "futuristic cityscape at sunset",
    "model": "9000:FLUX1.1-ultra",
    "image_count": 1
})
```

### 3. Puppeteer MCP - Web Automation
**Capabilities:**
- Automate web interactions
- Take screenshots of websites
- Fill forms and submit data
- Test web applications
- Scrape web content

**Example Usage:**
```python
# Automate a web task
await mcp_client.execute_mcp_tool("puppeteer", "navigate", {
    "url": "https://example.com"
})
await mcp_client.execute_mcp_tool("puppeteer", "fill", {
    "selector": "#email",
    "value": "user@example.com"
})
```

### 4. PostgreSQL MCP - Database Operations
**Capabilities:**
- Execute SQL queries
- Generate analytics reports
- Data visualization
- Performance monitoring

**Example Usage:**
```python
# Query user analytics
result = await mcp_client.execute_mcp_tool("postgres", "query", {
    "sql": "SELECT COUNT(*) as total_users, AVG(created_projects) as avg_projects FROM users WHERE created_at > NOW() - INTERVAL '30 days'"
})
```

### 5. Memory MCP - Knowledge Management
**Capabilities:**
- Create and manage knowledge graphs
- Store entity relationships
- Search and retrieve information
- Build contextual memory

**Example Usage:**
```python
# Store project information
await mcp_client.execute_mcp_tool("memory", "create_entities", {
    "entities": [{
        "name": "VeoGen Platform",
        "entityType": "Software Project",
        "observations": ["AI-powered creative platform", "Uses MCP architecture"]
    }]
})
```

### 6. User Manager MCP - Account Management
**Capabilities:**
- Create and manage user accounts
- Handle authentication flows
- Manage permissions and roles
- User analytics and reporting

### 7. Log Viewer MCP - System Monitoring
**Capabilities:**
- Access system logs
- Filter and search log entries
- Generate monitoring reports
- Alert on error patterns

## Chat Partner Action Framework

### Workflow Orchestration
```python
class ChatActionOrchestrator:
    def __init__(self, mcp_client: MCPClientManager):
        self.mcp_client = mcp_client
        
    async def process_user_intent(self, message: str, context: Dict[str, Any]):
        """Analyze user message and execute appropriate MCP actions"""
        
        # Intent analysis
        if "create 3d model" in message.lower():
            return await self.handle_3d_creation(message, context)
        elif "generate image" in message.lower():
            return await self.handle_image_generation(message, context)
        elif "automate website" in message.lower():
            return await self.handle_web_automation(message, context)
        elif "query database" in message.lower():
            return await self.handle_database_query(message, context)
        
    async def handle_3d_creation(self, prompt: str, context: Dict[str, Any]):
        """Handle 3D model creation requests"""
        # Extract model description
        model_prompt = self.extract_model_description(prompt)
        
        # Create 3D model
        model_result = await self.mcp_client.execute_mcp_tool("blender", "create_model", {
            "prompt": model_prompt,
            "style": context.get("preferred_style", "realistic")
        })
        
        # Optional: Generate preview image
        preview_result = await self.mcp_client.execute_mcp_tool("blender", "render_preview", {
            "model_id": model_result["model_id"],
            "angle": "isometric"
        })
        
        return {
            "action": "3d_model_created",
            "model_file": model_result["file_path"],
            "preview_image": preview_result["image_url"],
            "message": f"Created 3D model: {model_prompt}"
        }
```

## Integration Patterns

### 1. Sequential Actions
```python
async def create_product_showcase(product_name: str):
    """Create a complete product showcase"""
    
    # Step 1: Generate product image
    image_result = await mcp_client.execute_mcp_tool("everart", "generate_image", {
        "prompt": f"professional product photo of {product_name}",
        "model": "7000:Recraft-Real"
    })
    
    # Step 2: Create 3D model
    model_result = await mcp_client.execute_mcp_tool("blender", "create_model", {
        "prompt": f"3D model of {product_name}",
        "reference_image": image_result["image_url"]
    })
    
    # Step 3: Store in knowledge base
    await mcp_client.execute_mcp_tool("memory", "create_entities", {
        "entities": [{
            "name": product_name,
            "entityType": "Product",
            "observations": [f"Has 3D model: {model_result['model_id']}", f"Has image: {image_result['image_id']}"]
        }]
    })
    
    return {
        "product_name": product_name,
        "image_url": image_result["image_url"],
        "model_file": model_result["file_path"],
        "stored_in_memory": True
    }
```

### 2. Parallel Actions
```python
async def multi_format_content_creation(prompt: str):
    """Create content in multiple formats simultaneously"""
    
    tasks = [
        mcp_client.execute_mcp_tool("everart", "generate_image", {
            "prompt": prompt,
            "model": "5000:FLUX1.1"
        }),
        mcp_client.execute_mcp_tool("blender", "create_model", {
            "prompt": prompt,
            "style": "realistic"
        })
    ]
    
    image_result, model_result = await asyncio.gather(*tasks)
    
    return {
        "image": image_result,
        "model": model_result,
        "execution_time": "parallel"
    }
```

## Configuration Management

### Environment Setup
```bash
# .env configuration for MCP servers
MCP_BLENDER_PATH=./mcp-servers/blender-mcp
MCP_EVERART_API_KEY=your_everart_key
MCP_POSTGRES_URL=postgresql://user:pass@localhost:5432/veogen
MCP_MEMORY_STORAGE_PATH=./data/memory
```

### Server Initialization
```python
# backend/app/main.py
from app.services.mcp_client_service import MCPClientManager

@app.on_event("startup")
async def startup_event():
    app.state.mcp_client = MCPClientManager()
    
    # Pre-initialize critical MCPs
    await app.state.mcp_client.initialize_mcp("memory")
    await app.state.mcp_client.initialize_mcp("postgres")
    
    logger.info("MCP client services initialized")
```

## Security and Access Control

### MCP Permission System
```python
class MCPPermissionManager:
    def __init__(self):
        self.user_permissions = {
            "admin": ["all_mcps"],
            "premium": ["blender", "everart", "puppeteer", "memory"],
            "basic": ["everart", "memory"],
            "guest": ["memory"]
        }
    
    async def check_mcp_access(self, user_role: str, mcp_name: str) -> bool:
        """Check if user has access to specific MCP"""
        allowed_mcps = self.user_permissions.get(user_role, [])
        return "all_mcps" in allowed_mcps or mcp_name in allowed_mcps
```

## Monitoring and Observability

### MCP Health Monitoring
```python
class MCPHealthMonitor:
    async def check_mcp_health(self, mcp_name: str) -> Dict[str, Any]:
        """Monitor MCP server health"""
        try:
            session = await mcp_client.initialize_mcp(mcp_name)
            tools = await session.list_tools()
            
            return {
                "status": "healthy",
                "available_tools": len(tools),
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
```

## API Endpoints

### MCP Action Endpoints
```python
# backend/app/routers/mcp_actions.py
from fastapi import APIRouter, Depends
from app.services.mcp_client_service import MCPClientManager

router = APIRouter(prefix="/api/v1/mcp", tags=["mcp"])

@router.post("/execute")
async def execute_mcp_action(
    action_request: MCPActionRequest,
    mcp_client: MCPClientManager = Depends(get_mcp_client)
):
    """Execute an MCP action"""
    result = await mcp_client.execute_mcp_tool(
        action_request.mcp_name,
        action_request.tool_name,
        action_request.arguments
    )
    return {"status": "success", "result": result}

@router.get("/available")
async def list_available_mcps(
    mcp_client: MCPClientManager = Depends(get_mcp_client)
):
    """List all available MCPs and their capabilities"""
    return mcp_client.available_mcps

@router.get("/health")
async def mcp_health_status(
    mcp_client: MCPClientManager = Depends(get_mcp_client)
):
    """Get health status of all MCP servers"""
    health_monitor = MCPHealthMonitor()
    statuses = {}
    
    for mcp_name in mcp_client.available_mcps.keys():
        statuses[mcp_name] = await health_monitor.check_mcp_health(mcp_name)
    
    return statuses
```

## Frontend Integration

### MCP Action Components
```javascript
// frontend/src/components/MCPActionPanel.js
import React, { useState, useEffect } from 'react';
import { executeMAGCPAction, getAvailableMCPs } from '../services/mcpService';

const MCPActionPanel = () => {
    const [availableMCPs, setAvailableMCPs] = useState({});
    const [selectedMCP, setSelectedMCP] = useState('');
    const [actionHistory, setActionHistory] = useState([]);

    useEffect(() => {
        loadAvailableMCPs();
    }, []);

    const loadAvailableMCPs = async () => {
        const mcps = await getAvailableMCPs();
        setAvailableMCPs(mcps);
    };

    const executeAction = async (mcpName, toolName, arguments) => {
        try {
            const result = await executeMCPAction({
                mcp_name: mcpName,
                tool_name: toolName,
                arguments: arguments
            });
            
            setActionHistory(prev => [...prev, {
                timestamp: new Date().toISOString(),
                mcp: mcpName,
                tool: toolName,
                result: result
            }]);
            
            return result;
        } catch (error) {
            console.error('MCP action failed:', error);
            throw error;
        }
    };

    return (
        <div className="mcp-action-panel">
            <h3>Available MCP Services</h3>
            {Object.entries(availableMCPs).map(([name, config]) => (
                <div key={name} className="mcp-service">
                    <h4>{name}</h4>
                    <div className="capabilities">
                        {config.capabilities.map(cap => (
                            <span key={cap} className="capability-tag">{cap}</span>
                        ))}
                    </div>
                </div>
            ))}
            
            <div className="action-history">
                <h4>Recent Actions</h4>
                {actionHistory.slice(-5).map((action, index) => (
                    <div key={index} className="action-item">
                        <span className="timestamp">{new Date(action.timestamp).toLocaleTimeString()}</span>
                        <span className="action">{action.mcp}.{action.tool}</span>
                        <span className="status">✓</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default MCPActionPanel;
```

## Example Workflows

### 1. Complete Product Development
```python
async def product_development_workflow(product_idea: str):
    """Complete product development from idea to prototype"""
    
    # Research phase
    market_research = await mcp_client.execute_mcp_tool("puppeteer", "scrape_market_data", {
        "search_term": product_idea,
        "sources": ["amazon", "alibaba", "etsy"]
    })
    
    # Design phase
    concept_images = await mcp_client.execute_mcp_tool("everart", "generate_image", {
        "prompt": f"product concept for {product_idea}",
        "model": "7000:Recraft-Real",
        "image_count": 3
    })
    
    # 3D modeling phase
    prototype_model = await mcp_client.execute_mcp_tool("blender", "create_model", {
        "prompt": product_idea,
        "reference_images": concept_images["image_urls"]
    })
    
    # Documentation phase
    await mcp_client.execute_mcp_tool("memory", "create_entities", {
        "entities": [{
            "name": f"Product: {product_idea}",
            "entityType": "Product Development",
            "observations": [
                f"Market research completed",
                f"Concept images generated: {len(concept_images['image_urls'])}",
                f"3D prototype created: {prototype_model['model_id']}",
                f"Development status: Complete"
            ]
        }]
    })
    
    return {
        "status": "complete",
        "market_data": market_research,
        "concept_images": concept_images["image_urls"],
        "prototype_file": prototype_model["file_path"],
        "documentation_stored": True
    }
```

### 2. Automated Testing Pipeline
```python
async def automated_testing_workflow(app_url: str):
    """Automated testing of web applications"""
    
    # Visual testing
    screenshots = await mcp_client.execute_mcp_tool("puppeteer", "screenshot", {
        "url": app_url,
        "viewports": ["desktop", "tablet", "mobile"]
    })
    
    # Functional testing
    test_results = await mcp_client.execute_mcp_tool("puppeteer", "run_test_suite", {
        "url": app_url,
        "test_scenarios": ["login", "navigation", "form_submission"]
    })
    
    # Store results
    await mcp_client.execute_mcp_tool("postgres", "query", {
        "sql": """
        INSERT INTO test_results (app_url, test_date, screenshots, results, status)
        VALUES (%s, NOW(), %s, %s, %s)
        """,
        "params": [app_url, screenshots, test_results, "completed"]
    })
    
    return {
        "test_status": "completed",
        "screenshots": screenshots,
        "test_results": test_results,
        "stored_in_database": True
    }
```

## Performance Optimization

### Connection Pooling
```python
class MCPConnectionPool:
    def __init__(self, max_connections_per_mcp: int = 5):
        self.pools = {}
        self.max_connections = max_connections_per_mcp
    
    async def get_session(self, mcp_name: str) -> ClientSession:
        """Get an available session from the pool"""
        if mcp_name not in self.pools:
            self.pools[mcp_name] = asyncio.Queue(maxsize=self.max_connections)
            # Pre-populate with connections
            for _ in range(self.max_connections):
                session = await self.create_session(mcp_name)
                await self.pools[mcp_name].put(session)
        
        return await self.pools[mcp_name].get()
    
    async def return_session(self, mcp_name: str, session: ClientSession):
        """Return session to the pool"""
        await self.pools[mcp_name].put(session)
```

## Troubleshooting Guide

### Common Issues

1. **MCP Server Not Responding**
   - Check if the MCP server process is running
   - Verify network connectivity
   - Check server logs for errors

2. **Permission Denied**
   - Verify user has access to the requested MCP
   - Check API keys and authentication
   - Review permission configuration

3. **Tool Not Found**
   - Ensure MCP server is properly initialized
   - Verify tool name spelling
   - Check MCP server version compatibility

### Debug Mode
```python
# Enable debug mode for MCP communications
import logging
logging.getLogger("mcp").setLevel(logging.DEBUG)
```

## Future Expansions

### Planned MCP Integrations
- **OBS MCP**: Live streaming and recording automation
- **CNC MCP**: Computer-controlled manufacturing
- **Arduino MCP**: IoT device control
- **Cryptocurrency MCP**: Blockchain interactions
- **Email MCP**: Automated email management
- **Calendar MCP**: Schedule management
- **Social Media MCP**: Content publishing automation

This MCP client architecture transforms VeoGen into a comprehensive action platform where conversations naturally trigger real-world outcomes across multiple domains. 