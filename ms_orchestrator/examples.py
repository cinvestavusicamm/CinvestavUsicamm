"""Example API requests for ms_orchestrator testing."""

import httpx
import asyncio
import json
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────

ORCHESTRATOR_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

# ─────────────────────────────────────────────────────────────────────
# Example Requests
# ─────────────────────────────────────────────────────────────────────


async def health_check():
    """Check orchestrator health."""
    print("\n" + "=" * 70)
    print("1. HEALTH CHECK")
    print("=" * 70)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ORCHESTRATOR_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")


async def get_status():
    """Get orchestrator status."""
    print("\n" + "=" * 70)
    print("2. GET STATUS")
    print("=" * 70)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ORCHESTRATOR_URL}/status")
        print(f"Status: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")


async def validate_process():
    """Validate a process."""
    print("\n" + "=" * 70)
    print("3. VALIDATE PROCESS")
    print("=" * 70)

    payload = {
        "process_description": "Docente de Matemáticas evaluando desempeño de estudiantes en examen final",
        "rules_context": {
            "course_id": "MAT101",
            "semester": "2024-1",
            "evaluation_type": "summative",
            "department": "Matemáticas",
        },
        "metadata": {
            "source": "escalafon_web",
            "user_id": "prof_123",
            "timestamp": datetime.utcnow().isoformat(),
        },
    }

    print(f"Payload:\n{json.dumps(payload, indent=2)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ORCHESTRATOR_URL}/orchestrate/validation/validate",
            json=payload,
            headers=HEADERS,
        )
        print(f"Status: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")


async def validate_batch():
    """Validate multiple processes."""
    print("\n" + "=" * 70)
    print("4. BATCH VALIDATION")
    print("=" * 70)

    payload = [
        {
            "process_description": "Proceso de evaluación 1",
            "rules_context": {"course_id": "MAT101"},
        },
        {
            "process_description": "Proceso de evaluación 2",
            "rules_context": {"course_id": "ENG102"},
        },
        {
            "process_description": "Proceso de evaluación 3",
            "rules_context": {"course_id": "SCI103"},
        },
    ]

    print(f"Validating {len(payload)} processes...")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ORCHESTRATOR_URL}/orchestrate/validation/validate-batch",
            json=payload,
            headers=HEADERS,
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Successfully validated: {result.get('data', {}).get('count', 0)} processes")
        print(f"Response:\n{json.dumps(result, indent=2)}")


async def get_workflow_templates():
    """Get available workflow templates."""
    print("\n" + "=" * 70)
    print("5. GET WORKFLOW TEMPLATES")
    print("=" * 70)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ORCHESTRATOR_URL}/orchestrate/workflows/templates"
        )
        print(f"Status: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")


async def execute_workflow_sequential():
    """Execute a workflow with sequential steps."""
    print("\n" + "=" * 70)
    print("6. EXECUTE SEQUENTIAL WORKFLOW")
    print("=" * 70)

    payload = {
        "workflow_id": "wf_teacher_eval_001",
        "workflow_name": "Teacher Evaluation Pipeline",
        "parallel": False,
        "steps": [
            {
                "service": "validation",
                "action": "validate_process",
                "parameters": {
                    "process_description": "Docente evaluando desempeño académico",
                    "rules_context": {"course_id": "MAT101", "type": "teaching"},
                },
            },
            {
                "service": "backend_api",
                "action": "analyze_content",
                "parameters": {
                    "content": "Análisis de resultados de evaluación docente",
                    "analysis_type": "rag",
                    "context": {"model": "phi-3"},
                },
            },
            {
                "service": "database",
                "action": "store",
                "parameters": {
                    "collection": "evaluations",
                    "data": {
                        "type": "teacher_evaluation",
                        "status": "completed",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            },
        ],
    }

    print(f"Executing workflow: {payload['workflow_name']}")
    print(f"Steps: {len(payload['steps'])} (sequential)")

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{ORCHESTRATOR_URL}/orchestrate/workflows/execute",
            json=payload,
            headers=HEADERS,
        )
        print(f"Status: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")


async def execute_workflow_parallel():
    """Execute a workflow with parallel steps."""
    print("\n" + "=" * 70)
    print("7. EXECUTE PARALLEL WORKFLOW")
    print("=" * 70)

    payload = {
        "workflow_id": "wf_parallel_001",
        "workflow_name": "Parallel Processing Pipeline",
        "parallel": True,
        "steps": [
            {
                "service": "validation",
                "action": "validate_process",
                "parameters": {
                    "process_description": "Validación paralela 1",
                    "rules_context": {"id": "1"},
                },
            },
            {
                "service": "backend_api",
                "action": "analyze_content",
                "parameters": {
                    "content": "Análisis paralelo 1",
                    "analysis_type": "classification",
                },
            },
            {
                "service": "database",
                "action": "retrieve",
                "parameters": {
                    "collection": "results",
                    "result_id": "res_123",
                },
            },
        ],
    }

    print(f"Executing workflow: {payload['workflow_name']}")
    print(f"Steps: {len(payload['steps'])} (parallel)")

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{ORCHESTRATOR_URL}/orchestrate/workflows/execute",
            json=payload,
            headers=HEADERS,
        )
        print(f"Status: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")


# ─────────────────────────────────────────────────────────────────────
# Main Test Runner
# ─────────────────────────────────────────────────────────────────────


async def run_all_tests():
    """Run all test examples."""
    print("\n" + "🎼" * 35)
    print("MS_ORCHESTRATOR - API TESTING EXAMPLES")
    print("🎼" * 35)

    try:
        await health_check()
        await get_status()
        await get_workflow_templates()

        # Validation examples
        await validate_process()
        await validate_batch()

        # Workflow examples
        await execute_workflow_sequential()
        await execute_workflow_parallel()

        print("\n" + "=" * 70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback

        traceback.print_exc()


async def interactive_mode():
    """Interactive testing mode."""
    print("\n" + "=" * 70)
    print("MS_ORCHESTRATOR - INTERACTIVE TEST MODE")
    print("=" * 70)
    print("\nAvailable commands:")
    print("1. health - Check health status")
    print("2. status - Get orchestrator status")
    print("3. validate - Validate a single process")
    print("4. batch - Validate multiple processes")
    print("5. templates - Get workflow templates")
    print("6. workflow-seq - Execute sequential workflow")
    print("7. workflow-par - Execute parallel workflow")
    print("0. exit - Exit interactive mode")

    while True:
        cmd = input("\nEnter command (or 'help' for list): ").strip().lower()

        if cmd == "0" or cmd == "exit":
            break
        elif cmd == "1" or cmd == "health":
            await health_check()
        elif cmd == "2" or cmd == "status":
            await get_status()
        elif cmd == "3" or cmd == "validate":
            await validate_process()
        elif cmd == "4" or cmd == "batch":
            await validate_batch()
        elif cmd == "5" or cmd == "templates":
            await get_workflow_templates()
        elif cmd == "6" or cmd == "workflow-seq":
            await execute_workflow_sequential()
        elif cmd == "7" or cmd == "workflow-par":
            await execute_workflow_parallel()
        else:
            print("Unknown command. Type 'help' for list.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(run_all_tests())
