#!/usr/bin/env bash
# Verify Trivial Todo App Installation
# Runs basic smoke tests to ensure the app is installed and working correctly

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test directory - use a temp directory to avoid interfering with user's todos
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"

echo "🧪 Verifying Trivial Todo App installation..."
echo ""

# Cleanup function
cleanup() {
    cd - > /dev/null
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

# Test 1: Check if todo command exists
echo -n "✓ Checking if 'todo' command is available... "
if command -v todo &> /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "  Error: 'todo' command not found"
    echo "  Please install the app with: pip install ."
    exit 1
fi

# Test 2: Check help command
echo -n "✓ Checking help command... "
if todo --help &> /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "  Error: 'todo --help' failed"
    exit 1
fi

# Test 3: List empty todos
echo -n "✓ Listing empty todos... "
OUTPUT=$(todo list)
if [[ "$OUTPUT" == "No todos found" ]]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "  Expected: 'No todos found'"
    echo "  Got: '$OUTPUT'"
    exit 1
fi

# Test 4: Add a todo
echo -n "✓ Adding a todo... "
OUTPUT=$(todo add "Test todo item")
if [[ "$OUTPUT" == 'Added todo #1: "Test todo item"' ]]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "  Expected: 'Added todo #1: \"Test todo item\"'"
    echo "  Got: '$OUTPUT'"
    exit 1
fi

# Test 5: List todos with one item
echo -n "✓ Listing todos... "
OUTPUT=$(todo list)
if [[ "$OUTPUT" == "[ ] #1: Test todo item" ]]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "  Expected: '[ ] #1: Test todo item'"
    echo "  Got: '$OUTPUT'"
    exit 1
fi

# Test 6: Mark todo as done
echo -n "✓ Marking todo as done... "
OUTPUT=$(todo done 1)
if [[ "$OUTPUT" == 'Marked todo #1 as done: "Test todo item"' ]]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "  Expected: 'Marked todo #1 as done: \"Test todo item\"'"
    echo "  Got: '$OUTPUT'"
    exit 1
fi

# Test 7: Verify todo is marked as done
echo -n "✓ Verifying todo is done... "
OUTPUT=$(todo list)
if [[ "$OUTPUT" == "[✓] #1: Test todo item" ]]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "  Expected: '[✓] #1: Test todo item'"
    echo "  Got: '$OUTPUT'"
    exit 1
fi

# Test 8: Add multiple todos
echo -n "✓ Adding multiple todos... "
todo add "Second todo" > /dev/null
todo add "Third todo" > /dev/null
OUTPUT=$(todo list | wc -l | tr -d ' ')
if [[ "$OUTPUT" == "3" ]]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "  Expected 3 todos, got $OUTPUT"
    exit 1
fi

# Test 9: Check JSON file was created
echo -n "✓ Checking todos.json file... "
if [[ -f "todos.json" ]]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "  Error: todos.json file not found"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All tests passed!${NC}"
echo ""
echo "Your Trivial Todo App installation is working correctly."
echo ""
echo "Next steps:"
echo "  • Read the quickstart guide: docs/QUICKSTART.md"
echo "  • Start using: todo add \"Your first real todo\""
echo "  • Get help anytime: todo --help"
