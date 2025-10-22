# traffic-api

FastAPI template with PostgreSQL, Couchbase, Temporal, and Twilio support - designed for instant hot reload development.

## Development Notes

**The server runs with hot reload enabled** - Your changes are automatically applied when you save files. No manual restarts needed.

**ALWAYS check logs after making changes**: After any code change, verify it worked by checking the server logs:
```mcp
__polytope__get_container_logs(container: traffic-api, limit: 50)
```
Look for import errors, syntax errors, or runtime exceptions. The hot reload will show if your code loaded successfully or if there are any errors.

**Note**: If this project was created using the `add-api` tool, your API service runs in a container that you can access and observe through MCP commands.

## Quick Start

```mcp
# Check service status
__polytope__list_services()

# View recent logs
__polytope__get_container_logs(container: traffic-api, limit: 50)

# Test the API
curl http://localhost:3030/health
```

## API Endpoints

### Active Endpoints
- Health check: `GET /health` - Comprehensive health check with service status

### Example Endpoints (commented out)
The template includes commented-out example routes for:
- PostgreSQL user management
- Couchbase user operations
- Temporal workflow execution
- Twilio SMS sending

Uncomment and adapt these examples in `src/backend/routes/base.py` as needed.

## Setting Up Features

### PostgreSQL Database
1. Enable in `src/backend/conf.py`:
```python
USE_POSTGRES = True
```

2. Check logs to verify connection:
```mcp
__polytope__get_container_logs(container: traffic-api, limit: 50)
```

3. Test database health via health endpoint:
```bash
curl http://localhost:3030/health
```

4. Add database routes in `src/backend/routes/base.py`:
```python
from ..utils import DBSession

@router.post("/test-db")
async def test_database(session: DBSession):
    # DBSession auto-commits - NEVER call session.commit()
    return {"status": "connected"}
```

### Authentication
1. Enable: `USE_AUTH = True` in `conf.py`
2. Configure JWT authentication in environment/config (JWK URL, audience, etc.)
3. Protect any route by adding `RequestPrincipal` as a dependency - this validates JWT tokens from Authorization headers:
```python
from ..utils import RequestPrincipal

@router.get("/protected")
async def protected_route(principal: RequestPrincipal):
    # principal.claims contains the decoded JWT claims
    return {"claims": principal.claims}
```
4. Clients must send requests with `Authorization: Bearer <jwt-token>` header

### Temporal Workflows
1. Enable: `USE_TEMPORAL = True` in `conf.py`
2. Add workflows to `src/backend/workflows/examples.py`
3. Register workflows and activities in `src/backend/workflows/__init__.py`
4. Uncomment workflow routes in `src/backend/routes/base.py`

### Couchbase

Quick Setup - ALWAYS follow this pattern for new Couchbase collections:

1. Enable: `USE_COUCHBASE = True` in `conf.py`
2. Add desired collections - Run this tool:
   ```mcp
   __polytope__run(module: "traffic-api-add-couchbase-collection", args: {"name": "collection-name"})
   ```
   During initial setup, finish and verify this step before adding further services to the project.
3. Check container logs to verify success:
   ```mcp
   __polytope__get_container_logs(container: traffic-api, limit: 50)
   ```
4. Read the generated file at: `src/backend/couchbase/collections/<collection_name>.py`
5. Customize the model in the generated file (DO NOT create manually)
6. Uncomment example routes in `routes/base.py`

### SMS/Twilio
1. Set Twilio environment variables
2. Enable: `USE_TWILIO = True` in `conf.py`
3. Uncomment SMS routes in `routes/base.py`

## Development Workflow

1. **Make changes** - Edit any `.py` file
2. **Check logs immediately**:
   ```mcp
   __polytope__get_container_logs(container: traffic-api, limit: 50)
   ```
3. **Test changes** - `curl http://localhost:3030/your-route`
4. **Fix errors before continuing** - Don't move on until it works

## Key Files

- `src/backend/conf.py` - Feature toggles and configuration
- `src/backend/routes/base.py` - Add your API endpoints here
- `src/backend/routes/utils.py` - Database helpers (DBSession, RequestPrincipal)
- `src/backend/workflows/` - Temporal workflow definitions
- `polytope.yml` - Container and environment configuration

## Debugging

**Always start with logs when something doesn't work:**
```mcp
__polytope__get_container_logs(container: traffic-api, limit: 100)
```

Common checks:
1. **Service running**: `__polytope__list_services()`
2. **Health endpoint**: `curl http://localhost:3030/health`
3. **Configuration**: Check feature flags in `conf.py`
4. **Hot reload status**: Look for reload messages in logs

**Critical**: Hot reload means instant feedback - use it! Always check logs after saving files.
