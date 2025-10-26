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
    priority: str = "med",
    tags: Optional[list[str]] = None
) -> str:
    """
    Store a memory or note in the Remembar database.
    
    Parameters:
    - text (str): The memory or information to store
    - priority (str): Priority level - 'low', 'med', or 'high' (default: 'med')
    - tags (list[str], optional): List of tags to categorize the memory
    
    Returns:
    - str: Confirmation message with note ID
    """
    try:
        # Validate priority
        if priority not in ["low", "med", "high"]:
            priority = "med"
        
        # Prepare request payload matching ChromaDB /add_note schema
        payload = {
            "tenant_id": TENANT_ID,
            "text": text,
            "modality": "typed",
            "priority": priority,
            "tags": tags if tags else [],
            "linked_entity": None
        }
        
        # Call ChromaDB /add_note endpoint
        response = requests.post(
            f"{CHROMADB_URL}/add_note",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                note_id = data.get("note_id", "unknown")
                return f"✓ Memory saved successfully! (ID: {note_id})\n\nI'll remember: {text}"
            else:
                return "Failed to save memory. Please try again."
        else:
            return f"Error connecting to memory database. Status: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return f"Network error: Unable to reach memory database. Please check your connection."
    except Exception as e:
        return f"Error saving memory: {str(e)}"


@mcp.tool(description="Search for memories and information in Remembar. Use this when the user asks questions like 'where are my keys?', 'when did I...?', or wants to recall any stored information.")
def search_memory(
    query: str,
    n_results: int = 5
) -> str:
    """
    Search for memories and information using natural language.
    
    Parameters:
    - query (str): Natural language question or search term
    - n_results (int): Number of results to return (default: 5)
    
    Returns:
    - str: Formatted search results with relevant memories
    """
    try:
        # Prepare request payload matching ChromaDB /search_semantic schema
        payload = {
            "tenant_id": TENANT_ID,
            "query_text": query,
            "collections": ["entities_stream_v1", "user_notes_v1"],
            "n_results": min(n_results, 10)  # Cap at 10 results
        }
        
        # Call ChromaDB /search_semantic endpoint
        response = requests.post(
            f"{CHROMADB_URL}/search_semantic",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                results = data.get("results", [])
                
                if not results:
                    return f"I couldn't find any memories matching '{query}'. Try rephrasing or add this as a new memory!"
                
                # Format results for messaging interface
                response_text = f"Found {len(results)} relevant memories:\n\n"
                
                for i, result in enumerate(results[:5], 1):
                    doc = result.get("document", "")
                    distance = result.get("distance", 0)
                    
                    # Show most relevant results (lower distance = more relevant)
                    confidence = "🔥" if distance < 0.5 else "✓"
                    response_text += f"{confidence} {doc}\n"
                    
                    # Add context from metadata if available
                    metadata = result.get("metadata", {})
                    if "frame_ts" in metadata:
                        response_text += "   (from visual memory)\n"
                    elif "note_id" in metadata:
                        response_text += "   (from your notes)\n"
                    
                    response_text += "\n"
                
                return response_text.strip()
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
            f"{CHROMADB_URL}/healthz",
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

