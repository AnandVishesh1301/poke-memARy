<!-- 6e9bbd53-3c77-42df-bd0c-720fdc76804d bf756f46-4817-4ae5-9aa0-f134196d3550 -->
# Poke MCP Server for Remembar

## Overview

Create an MCP server using FastMCP that connects to your deployed ChromaDB at `https://memary-chromadb.ngrok-free.app/` to provide two core operations for Alzheimer's patients via messaging:

1. **Add Memory Tool** - Store information/notes directly to ChromaDB
2. **Search Memory Tool** - Find information using natural language queries

## Project Structure

Create a new directory `poke-mcp-server/` with:

```
poke-mcp-server/
├── src/
│   └── server.py          # Main FastMCP server with tools
├── requirements.txt        # Python dependencies
├── render.yaml            # Render deployment config
├── .env.example           # Environment variables template
└── README.md              # Setup and usage instructions
```

## Implementation Steps

### 1. Core Files

**requirements.txt**

- fastmcp
- requests
- python-dotenv
- uvicorn

**src/server.py**

- Initialize FastMCP server with name "RemembarMCP"
- Create `add_memory` tool that calls ChromaDB's `/add_note` endpoint
  - Parameters: text (the memory to store), priority (optional: low/med/high), tags (optional list)
  - Uses tenant_id: "default_user" (since no auth for MVP)
  - Returns confirmation with note_id
- Create `search_memory` tool that calls ChromaDB's `/search_semantic` endpoint
  - Parameters: query (natural language question)
  - Searches across entities_stream_v1 and user_notes_v1 collections
  - Returns top 5 relevant results with formatted output
- Add health check endpoint for monitoring

**render.yaml**

- Configure Python 3.11 runtime
- Set start command: `python src/server.py`
- Define environment variable placeholders for CHROMADB_URL

**.env.example**

- CHROMADB_URL=https://memary-chromadb.ngrok-free.app
- PORT=8000
- TENANT_ID=default_user

### 2. API Integration Details

**Add Memory Flow:**

```
User message → Poke → MCP add_memory tool → POST /add_note → ChromaDB
```

Request structure:

```python
{
  "tenant_id": "default_user",
  "text": "<user's message>",
  "modality": "typed",
  "priority": "med",
  "tags": []
}
```

**Search Memory Flow:**

```
User query → Poke → MCP search_memory tool → POST /search_semantic → ChromaDB
```

Request structure:

```python
{
  "tenant_id": "default_user",
  "query_text": "<user's question>",
  "collections": ["entities_stream_v1", "user_notes_v1"],
  "n_results": 5
}
```

### 3. Deployment Configuration

- Use Render Web Service (not background worker)
- Health check: GET /mcp (FastMCP automatically provides this)
- Environment: Python 3.11
- Region: Oregon (closest to ngrok endpoint if US-based)
- Auto-deploy from Git repository

### 4. Testing Strategy

Create simple manual tests:

- Test `/add_memory` with sample memory: "My keys are usually on the kitchen counter"
- Test `/search_memory` with query: "where are my keys?"
- Verify responses from ChromaDB are properly formatted for Poke
- Test via MCP Inspector locally before deploying

## Key Decisions

- **Tenant ID**: Use "default_user" for MVP (no multi-tenancy needed)
- **Collections**: Search both entities_stream_v1 and user_notes_v1 for comprehensive results
- **Error Handling**: Return user-friendly error messages if ChromaDB is unreachable
- **Response Format**: Keep responses concise and conversational for messaging interface
- **No Auth**: Skip authentication as specified (hackathon MVP)

## Integration with Poke

After deployment:

1. Get Render deployment URL (e.g., `https://remembar-mcp.onrender.com`)
2. Add MCP integration in Poke settings at `https://poke.com/settings/connections/integrations/new`
3. Provide MCP server URL with `/mcp` path
4. Test by sending messages to Poke number

## Future Enhancements (Post-Hackathon)

- Add `/search_last_seen` tool for specific object queries ("where are my glasses?")
- Multi-user support with phone number → tenant_id mapping
- Priority-based tagging (detect urgent information)
- Session management for conversation context
- Location-based queries using lat_lon_hash

### To-dos

- [ ] Create poke-mcp-server directory structure with all necessary files
- [ ] Implement FastMCP server with add_memory and search_memory tools in src/server.py
- [ ] Create requirements.txt with fastmcp, requests, python-dotenv, uvicorn
- [ ] Create render.yaml for Render deployment configuration
- [ ] Create README.md with setup instructions and usage guide