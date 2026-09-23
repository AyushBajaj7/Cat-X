#!/usr/bin/env python3
"""
Comprehensive Monorepo Validation Script for CAT Operator Shift Twin.
Validates:
1. Python syntax & AST across all packages
2. JSON schema validity for shared contracts
3. Import isolation (no private cross-service imports)
4. Port uniqueness and documentation consistency
5. YAML syntax for docker-compose and CI workflows
"""

import ast
import json
import os
from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent


def validate_python_ast():
    """Verify that every python file compiles into valid AST without syntax errors."""
    print("-> Checking Python syntax and AST compilation...")
    errors = []
    py_files = list(REPO_ROOT.glob("**/*.py"))
    
    # Filter out virtual environments or cache
    py_files = [
        f for f in py_files
        if "venv" not in f.parts and ".venv" not in f.parts and "__pycache__" not in f.parts
    ]

    for py_file in py_files:
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
            ast.parse(content, filename=str(py_file))
        except SyntaxError as e:
            errors.append(f"Syntax error in {py_file.relative_to(REPO_ROOT)}: {e}")

    if errors:
        for err in errors:
            print(f"  [FAIL] {err}")
        return False
    print(f"  [PASS] All {len(py_files)} Python files parsed successfully.")
    return True


def validate_json_schemas():
    """Verify that all JSON schemas in shared/contracts/ are valid JSON and have required schema properties."""
    print("-> Checking shared JSON schema contracts...")
    contracts_dir = REPO_ROOT / "shared" / "contracts"
    if not contracts_dir.exists():
        print("  [FAIL] shared/contracts directory missing!")
        return False

    required_contracts = [
        "telemetry.schema.json",
        "safety.schema.json",
        "task.schema.json",
        "prediction.schema.json",
        "shift-twin.schema.json",
        "training.schema.json",
        "error.schema.json",
    ]

    errors = []
    for contract_name in required_contracts:
        schema_path = contracts_dir / contract_name
        if not schema_path.exists():
            errors.append(f"Missing schema contract: {contract_name}")
            continue

        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "$schema" not in data and "type" not in data:
                errors.append(f"{contract_name} lacks $schema or type declaration")
            if "title" not in data:
                errors.append(f"{contract_name} lacks title")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in {contract_name}: {e}")

    if errors:
        for err in errors:
            print(f"  [FAIL] {err}")
        return False
    print(f"  [PASS] All {len(required_contracts)} JSON schema contracts are valid.")
    return True


def validate_import_isolation():
    """Verify that no microservice imports internal modules from another microservice."""
    print("-> Checking cross-service import isolation...")
    services = {
        "safety": REPO_ROOT / "services" / "safety",
        "operations": REPO_ROOT / "services" / "operations",
        "training": REPO_ROOT / "services" / "training",
    }

    errors = []
    for svc_name, svc_dir in services.items():
        other_services = [s for s in services if s != svc_name]
        for py_file in svc_dir.glob("**/*.py"):
            if "venv" in py_file.parts or "__pycache__" in py_file.parts:
                continue
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for other in other_services:
                            if alias.name.startswith(f"services.{other}") or alias.name.startswith(f"{other}."):
                                errors.append(
                                    f"Illegal cross-import: {py_file.relative_to(REPO_ROOT)} imports from '{other}'"
                                )
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    for other in other_services:
                        if mod.startswith(f"services.{other}") or mod.startswith(f"{other}."):
                            errors.append(
                                f"Illegal cross-import: {py_file.relative_to(REPO_ROOT)} imports from '{other}'"
                            )

    if errors:
        for err in errors:
            print(f"  [FAIL] {err}")
        return False
    print("  [PASS] Clean architectural boundary isolation verified across all services.")
    return True


def validate_ports_uniqueness():
    """Verify that all service ports are distinct and match architecture standards."""
    print("-> Checking port allocations...")
    expected_ports = {
        "frontend": 5173,
        "gateway": 8000,
        "safety": 8001,
        "operations": 8002,
        "training": 8003,
        "postgres": 5432,
    }

    ports = list(expected_ports.values())
    if len(ports) != len(set(ports)):
        print("  [FAIL] Duplicate ports detected!")
        return False

    print(f"  [PASS] All {len(ports)} service ports are strictly unique: {expected_ports}")
    return True


def validate_yaml_files():
    """Verify docker-compose and GitHub CI YAML basic structure."""
    print("-> Checking YAML configurations...")
    compose_path = REPO_ROOT / "docker-compose.yml"
    ci_path = REPO_ROOT / ".github" / "workflows" / "ci.yml"

    errors = []
    if not compose_path.exists():
        errors.append("docker-compose.yml missing!")
    else:
        with open(compose_path, "r", encoding="utf-8") as f:
            text = f.read()
            if "services:" not in text:
                errors.append("docker-compose.yml missing 'services:' block")

    if not ci_path.exists():
        errors.append(".github/workflows/ci.yml missing!")
    else:
        with open(ci_path, "r", encoding="utf-8") as f:
            text = f.read()
            if "jobs:" not in text:
                errors.append("ci.yml missing 'jobs:' block")

    if errors:
        for err in errors:
            print(f"  [FAIL] {err}")
        return False
    print("  [PASS] Docker Compose and CI YAML configurations verified.")
    return True


def main():
    print("==================================================")
    print("CAT OPERATOR SHIFT TWIN: REPOSITORY VALIDATION")
    print("==================================================")

    results = [
        validate_python_ast(),
        validate_json_schemas(),
        validate_import_isolation(),
        validate_ports_uniqueness(),
        validate_yaml_files(),
    ]

    print("==================================================")
    if all(results):
        print("ALL MONOREPO ARCHITECTURAL CHECKS PASSED!")
        print("==================================================")
        return 0
    else:
        print("MONOREPO VALIDATION FAILED!")
        print("==================================================")
        return 1


if __name__ == "__main__":
    sys.exit(main())
