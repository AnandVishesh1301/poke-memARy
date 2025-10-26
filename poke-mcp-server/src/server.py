#!/usr/bin/env python3
"""
Remembar MCP Server for Poke Integration
Enables Alzheimer's patients to add and search memories via messaging app
"""
import os
import requests
from fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Configuration
CHROMADB_URL = os.getenv("CHROMADB_URL", "https://memary-chromadb.ngrok-free.app")
TENANT_ID = os.getenv("TENANT_ID", "default_user")

# Initialize FastMCP
mcp = FastMCP("RemembarMCP")


@mcp.tool(description="Add a memory or note to Remembar. Use this when the user wants to remember something important like locations of items, appointments, or any information they want to store.")
def add_memory(
    text: str,
    session_id: str = "default"
) -> str:
    """
    Store a memory or note in the Remembar database.
    
    Parameters:
    - text (str): The memory or information to store
    - session_id (str): Session identifier (default: 'default')
    
    Returns:
    - str: Confirmation message with storage details
    """
    try:
        # Prepare request payload matching ChromaDB /store_text schema
        payload = {
            "text_summary": text,
            "session_id": session_id
        }
        
        # Call ChromaDB /store_text endpoint
        response = requests.post(
            f"{CHROMADB_URL}/store_text",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "ngrok-skip-browser-warning": "true"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                # Extract analysis details
                analysis = data.get("analysis", {})
                scene = analysis.get("scene", "No scene description")
                objects = analysis.get("objects", [])
                
                result = f"✓ Memory saved successfully!\n\n"
                result += f"📝 Scene: {scene}\n"
                
                if objects:
                    result += f"\n🎯 Detected {len(objects)} object(s):\n"
                    for obj in objects[:5]:  # Show first 5 objects
                        label = obj.get("label", "unknown")
                        color = obj.get("color")
                        if color and color != "null":
                            result += f"  • {label} ({color})\n"
                        else:
                            result += f"  • {label}\n"
                
                return result
            else:
                return "Failed to save memory. Please try again."
        else:
            return f"Error connecting to memory database. Status: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return "Network error: Unable to reach memory database. Please check your connection."
    except Exception as e:
        return f"Error saving memory: {str(e)}"


@mcp.tool(description="Search for memories and information in Remembar. Use this when the user asks questions like 'where are my keys?', 'when did I...?', or wants to recall any stored information.")
def search_memory(
    query: str,
    session_id: Optional[str] = None
) -> str:
    """
    Search for memories and information using natural language.
    
    Parameters:
    - query (str): Natural language question or search term
    - session_id (str, optional): Filter by session ID
    
    Returns:
    - str: Natural language answer with relevant memories
    """
    try:
        # Build query URL for GET /search endpoint
        url = f"{CHROMADB_URL}/search?query={requests.utils.quote(query)}"
        if session_id:
            url += f"&session_id={requests.utils.quote(session_id)}"
        
        # Call ChromaDB /search endpoint
        response = requests.get(
            url,
            headers={"ngrok-skip-browser-warning": "true"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                answer = data.get("answer", "")
                mode = data.get("mode", "")
                matches = data.get("matches", 0)
                tracked_item = data.get("tracked_item")
                
                if not answer:
                    return f"I couldn't find any memories matching '{query}'. Try rephrasing or add this as a new memory!"
                
                # Format natural language response
                result = f"🤖 {answer}\n"
                
                if matches > 0:
                    result += f"\n📊 Found {matches} relevant memories"
                    if mode:
                        result += f" (mode: {mode})"
                    result += "\n"
                
                if tracked_item:
                    result += f"\n📌 Tracked item: {tracked_item}\n"
                
                return result.strip()
            else:
                return "Failed to search memories. Please try again."
        else:
            return f"Error connecting to memory database. Status: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return "Network error: Unable to reach memory database. Please check your connection."
    except Exception as e:
        return f"Error searching memories: {str(e)}"


@mcp.tool(description="Get information about the Remembar MCP server including version and connection status")
def get_server_info() -> dict:
    """
    Get server information and health status.
    
    Returns:
    - dict: Server information including name, version, and ChromaDB status
    """
    try:
        # Check ChromaDB health
        health_response = requests.get(
            f"{CHROMADB_URL}/",
            headers={"ngrok-skip-browser-warning": "true"},
            timeout=5
        )
        chromadb_status = "connected" if health_response.status_code == 200 else "disconnected"
    except Exception:
        chromadb_status = "disconnected"
    
    return {
        "server_name": "RemembarMCP",
        "version": "1.0.0",
        "description": "Memory assistant for Alzheimer's patients",
        "chromadb_url": CHROMADB_URL,
        "chromadb_status": chromadb_status,
        "tenant_id": TENANT_ID,
        "features": ["add_memory", "search_memory"]
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"🧠 Starting Remembar MCP Server")
    print(f"   Host: {host}:{port}")
    print(f"   ChromaDB: {CHROMADB_URL}")
    print(f"   Tenant: {TENANT_ID}")
    print(f"   Ready for Poke integration!\n")
    
    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True
    )

