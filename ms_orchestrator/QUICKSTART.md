"""
QUICK START GUIDE - MS_ORCHESTRATOR

Get the orchestrator running in 5 minutes.
"""

# ─────────────────────────────────────────────────────────────────────
# OPTION 1: Docker (Fastest)
# ─────────────────────────────────────────────────────────────────────

"""
Step 1: Build the image
    docker build -t escalafon_orchestrator:latest .

Step 2: Run with docker-compose
    docker-compose up -d

Step 3: Check health
    curl http://localhost:8000/health

Step 4: Open API docs
    http://localhost:8000/docs
"""

# ─────────────────────────────────────────────────────────────────────
# OPTION 2: Local Development
# ─────────────────────────────────────────────────────────────────────

"""
Step 1: Create virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

Step 2: Install dependencies
    pip install -r requirements.txt

Step 3: Configure environment
    cp .env.example .env
    # Edit .env if needed (defaults work locally)

Step 4: Run the service
    uvicorn src.infrastructure.api.main:app --reload --port 8000

Step 5: Access the service
    http://localhost:8000/docs
"""

# ─────────────────────────────────────────────────────────────────────
# FIRST REQUESTS
# ─────────────────────────────────────────────────────────────────────

"""
1. Check Health:
    curl http://localhost:8000/health

2. Get Status:
    curl http://localhost:8000/status

3. Get Workflow Templates:
    curl http://localhost:8000/orchestrate/workflows/templates

4. Validate a Process:
    curl -X POST http://localhost:8000/orchestrate/validation/validate \
      -H "Content-Type: application/json" \
      -d '{
        "process_description": "Docente evaluando estudiantes",
        "rules_context": {"course_id": "MAT101"}
      }'

5. Execute a Workflow:
    curl -X POST http://localhost:8000/orchestrate/workflows/execute \
      -H "Content-Type: application/json" \
      -d '{
        "workflow_id": "wf_001",
        "workflow_name": "Test Workflow",
        "parallel": false,
        "steps": [
          {
            "service": "validation",
            "action": "validate_process",
            "parameters": {
              "process_description": "Test",
              "rules_context": {}
            }
          }
        ]
      }'
"""

# ─────────────────────────────────────────────────────────────────────
# KEY ENDPOINTS
# ─────────────────────────────────────────────────────────────────────

ENDPOINTS = {
    "Health & Status": [
        "GET /health - Check health of orchestrator and services",
        "GET /status - Get detailed orchestrator status",
    ],
    "Validation": [
        "POST /orchestrate/validation/validate - Validate a single process",
        "POST /orchestrate/validation/validate-batch - Validate multiple processes",
    ],
    "Workflows": [
        "POST /orchestrate/workflows/execute - Execute a workflow",
        "GET /orchestrate/workflows/templates - Get workflow templates",
    ],
}

# ─────────────────────────────────────────────────────────────────────
# COMMON ISSUES & SOLUTIONS
# ─────────────────────────────────────────────────────────────────────

"""
Issue: "Connection refused" when calling other services
Solution: Make sure other microservices are running:
    - ms_validation (port 8001)
    - ia_service_core (port 8003)
    - microservice_db (port 8002)
    Use "docker-compose up -d" from infrastructure directory

Issue: "Circuit breaker open" errors
Solution: Service is temporarily unavailable. It will recover automatically
    after CIRCUIT_BREAKER_RECOVERY_TIMEOUT (default 60s)

Issue: Logs are hard to read
Solution: Change LOG_FORMAT to 'text' in .env:
    LOG_FORMAT=text

Issue: Want to see what's happening
Solution: Enable debug logging:
    LOG_LEVEL=DEBUG
"""

# ─────────────────────────────────────────────────────────────────────
# ENVIRONMENT VARIABLES (Important)
# ─────────────────────────────────────────────────────────────────────

"""
VALIDATION_SERVICE_URL=http://localhost:8001          # Validation service
BACKEND_API_URL=http://localhost:8003                 # AI service
MICROSERVICE_DB_URL=http://localhost:8002             # Database service

SERVICE_TIMEOUT=30                                     # Request timeout (seconds)
RETRY_MAX_ATTEMPTS=3                                   # Retry attempts
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5                   # Failures before circuit opens

LOG_LEVEL=INFO                                         # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json                                        # json or text
"""

# ─────────────────────────────────────────────────────────────────────
# TEST WITH EXAMPLES
# ─────────────────────────────────────────────────────────────────────

"""
Run all example requests:
    python examples.py

Interactive testing:
    python examples.py interactive
"""

# ─────────────────────────────────────────────────────────────────────
# DOCUMENTATION
# ─────────────────────────────────────────────────────────────────────

"""
- API Documentation: http://localhost:8000/docs (Swagger UI)
- ReDoc Documentation: http://localhost:8000/redoc
- README.md - Full documentation
- ARCHITECTURE.md - Architecture decisions
- examples.py - Example API calls
"""

# ─────────────────────────────────────────────────────────────────────
# NEXT STEPS
# ─────────────────────────────────────────────────────────────────────

"""
1. Read README.md for comprehensive documentation
2. Explore API docs at /docs endpoint
3. Run examples.py to test endpoints
4. Check ARCHITECTURE.md for design decisions
5. Customize workflows for your use cases
"""

print(__doc__)
print("\nFor more information, see README.md")
