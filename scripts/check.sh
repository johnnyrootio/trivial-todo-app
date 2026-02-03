#!/bin/bash
set -euo pipefail

echo "=== Format check ==="
ruff format --check src/ tests/

echo ""
echo "=== Lint ==="
ruff check src/ tests/

echo ""
echo "=== Type check ==="
mypy src/

echo ""
echo "=== Tests ==="
pytest tests/ -v

echo ""
echo "✅ All checks passed!"
