# MCPB Test Considerations and Validation Strategy

## Testing Framework Requirements

### 1. MCP Protocol Compliance Testing

**Tool Response Validation**
```python
# Example test structure
import pytest
from mcp.testing import MCPTestClient

class TestCVMCPServer:
    @pytest.fixture
    def mcp_client(self):
        return MCPTestClient("cv_francisco_perez_sorrosal")

    def test_get_cv_tool_response_structure(self, mcp_client):
        """Validate get_cv tool returns properly structured response"""
        response = mcp_client.call_tool("get_cv")

        # Validate response structure
        assert "error" not in response
        assert "result" in response
        assert isinstance(response["result"], str)
        assert len(response["result"]) > 0

        # Validate markdown content structure
        content = response["result"]
        assert "Francisco Perez-Sorrosal" in content
        assert content.startswith("#") or "##" in content  # Has markdown headers
```

**Resource Access Validation**
```python
def test_cv_resource_accessibility(self, mcp_client):
    """Validate CV resource is accessible and returns valid content"""
    resource = mcp_client.get_resource("cvfps://full")

    assert resource is not None
    assert "Francisco Perez-Sorrosal" in resource
    assert len(resource) > 1000  # Reasonable CV length check
```

**Prompt Response Validation**
```python
def test_summary_prompt_generation(self, mcp_client):
    """Validate summary prompt generates expected content"""
    prompt = mcp_client.get_prompt("summary", {
        "depth_level": "brief",
        "context": "industry R&D role"
    })

    assert "Francisco Perez-Sorrosal" in prompt
    assert "brief" in prompt
    assert "industry R&D role" in prompt
```

### 2. Manifest Validation Testing

**Manifest Structure Validation**
```python
import json
import jsonschema

def test_manifest_schema_compliance():
    """Validate manifest.json follows MCPB specification"""
    with open("manifest.json", "r") as f:
        manifest = json.load(f)

    # Basic required fields
    required_fields = [
        "manifest_version", "name", "version", "description",
        "author", "server"
    ]
    for field in required_fields:
        assert field in manifest, f"Missing required field: {field}"

    # Server configuration validation
    server_config = manifest["server"]
    assert server_config["type"] == "python"
    assert "entry_point" in server_config
    assert "mcp_config" in server_config
```

**Bundle Integration Testing**
```python
def test_bundle_loadability():
    """Test that the bundle can be loaded by MCP host"""
    # Simulate bundle loading process
    # This would test actual MCPB loading mechanisms
    pass
```

### 3. Transport Mode Testing

**Stdio Transport Testing**
```python
import subprocess
import json

def test_stdio_transport():
    """Test MCP server via stdio transport"""
    process = subprocess.Popen(
        ["python", "src/cv_mcp_server/main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={"TRANSPORT": "stdio"}
    )

    # Send MCP initialization request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "1.0.0"}
    }

    stdout, stderr = process.communicate(json.dumps(init_request))
    assert process.returncode == 0

    response = json.loads(stdout)
    assert "result" in response
    assert "serverInfo" in response["result"]
```

**HTTP Transport Testing**
```python
import httpx
import asyncio

async def test_http_transport():
    """Test MCP server via streamable-http transport"""
    # Start server in HTTP mode
    process = subprocess.Popen([
        "python", "src/cv_mcp_server/main.py"
    ], env={
        "TRANSPORT": "streamable-http",
        "HOST": "localhost",
        "PORT": "8000"
    })

    await asyncio.sleep(2)  # Allow server to start

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "result" in data
            assert "tools" in data["result"]
    finally:
        process.terminate()
```

### 4. Production Readiness Testing

**Error Handling Validation**
```python
def test_error_handling_graceful_degradation():
    """Test server handles errors gracefully"""
    # Test missing PDF file
    # Test corrupted PDF file
    # Test network failures
    # Test invalid parameters
    pass

def test_resource_constraints():
    """Test server behavior under resource constraints"""
    # Test memory limits
    # Test CPU limits
    # Test disk space limits
    pass
```

**Performance Testing**
```python
import time
import concurrent.futures

def test_response_time_performance():
    """Test tool response times are within acceptable limits"""
    client = MCPTestClient("cv_francisco_perez_sorrosal")

    start_time = time.time()
    response = client.call_tool("get_cv")
    end_time = time.time()

    response_time = end_time - start_time
    assert response_time < 5.0, f"Response time too slow: {response_time}s"

def test_concurrent_request_handling():
    """Test server handles concurrent requests"""
    client = MCPTestClient("cv_francisco_perez_sorrosal")

    def make_request():
        return client.call_tool("get_cv")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [future.result() for future in futures]

    # All requests should succeed
    for result in results:
        assert "error" not in result
```

**Security Testing**
```python
def test_input_sanitization():
    """Test that tool inputs are properly sanitized"""
    client = MCPTestClient("cv_francisco_perez_sorrosal")

    # Test SQL injection attempts
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "../../../etc/passwd",
        "<script>alert('xss')</script>",
        "null\x00byte"
    ]

    for malicious_input in malicious_inputs:
        try:
            response = client.call_tool("summarize_cv", {
                "additional_instructions": malicious_input
            })
            # Should not crash or return sensitive information
            assert "error" not in response or "Invalid input" in response.get("error", {}).get("message", "")
        except Exception as e:
            # Should handle gracefully
            assert "Invalid input" in str(e)
```

### 5. Compatibility Testing

**Platform Compatibility**
```python
import platform

def test_platform_compatibility():
    """Test server works on different platforms"""
    current_platform = platform.system().lower()

    # Test on current platform
    client = MCPTestClient("cv_francisco_perez_sorrosal")
    response = client.call_tool("get_cv")
    assert "error" not in response

    # Platform-specific tests
    if current_platform == "darwin":
        # macOS specific tests
        pass
    elif current_platform == "linux":
        # Linux specific tests
        pass
    elif current_platform == "windows":
        # Windows specific tests
        pass
```

**Python Version Compatibility**
```python
import sys

def test_python_version_compatibility():
    """Test server works with supported Python versions"""
    assert sys.version_info >= (3, 11), "Requires Python 3.11+"

    # Test specific Python version features
    client = MCPTestClient("cv_francisco_perez_sorrosal")
    response = client.call_tool("get_cv")
    assert "error" not in response
```

### 6. Integration Testing

**Host Integration Testing**
```python
def test_claude_desktop_integration():
    """Test integration with Claude Desktop"""
    # This would test actual Claude Desktop integration
    # Load configuration from config/claude.json
    # Test server startup and communication
    pass

def test_third_party_mcp_client_integration():
    """Test integration with third-party MCP clients"""
    # Test with different MCP client implementations
    pass
```

**Bundle Lifecycle Testing**
```python
def test_bundle_installation():
    """Test MCPB installation process"""
    # Test bundle validation
    # Test dependency installation
    # Test configuration setup
    pass

def test_bundle_update():
    """Test MCPB update process"""
    # Test version compatibility
    # Test configuration migration
    # Test data preservation
    pass

def test_bundle_uninstallation():
    """Test MCPB uninstallation process"""
    # Test cleanup procedures
    # Test configuration removal
    # Test dependency cleanup
    pass
```

## Test Execution Strategy

### Continuous Integration Pipeline

```yaml
# .github/workflows/test.yml
name: MCPB Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: [3.11, 3.12]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio httpx

    - name: Run MCP Protocol Tests
      run: pytest tests/test_mcp_protocol.py -v

    - name: Run Transport Tests
      run: pytest tests/test_transports.py -v

    - name: Run Performance Tests
      run: pytest tests/test_performance.py -v

    - name: Run Security Tests
      run: pytest tests/test_security.py -v

    - name: Test Bundle Creation
      run: |
        # Test manifest validation
        python -m json.tool manifest.json
        # Test bundle creation (if tooling available)
```

### Local Development Testing

```bash
#!/bin/bash
# test_runner.sh

echo "Running MCPB Test Suite..."

# 1. Manifest validation
echo "Validating manifest.json..."
python -m json.tool manifest.json > /dev/null || exit 1

# 2. MCP protocol tests
echo "Running MCP protocol tests..."
pytest tests/test_mcp_protocol.py -v || exit 1

# 3. Transport tests
echo "Testing stdio transport..."
export TRANSPORT=stdio
python src/cv_mcp_server/main.py &
SERVER_PID=$!
sleep 2
kill $SERVER_PID

echo "Testing HTTP transport..."
export TRANSPORT=streamable-http
export PORT=8001
python src/cv_mcp_server/main.py &
SERVER_PID=$!
sleep 2
curl -f http://localhost:8001/health || echo "Health check failed"
kill $SERVER_PID

# 4. Performance tests
echo "Running performance tests..."
pytest tests/test_performance.py -v || exit 1

echo "All tests passed!"
```

## Critical Test Areas

### High Priority
1. **MCP Protocol Compliance**: Ensure all responses follow MCP specification
2. **Manifest Validation**: Verify manifest.json is valid and complete
3. **Transport Functionality**: Both stdio and HTTP transports work correctly
4. **Error Handling**: Graceful error handling and recovery

### Medium Priority
1. **Performance**: Response times and resource usage
2. **Security**: Input validation and sanitization
3. **Compatibility**: Platform and Python version compatibility
4. **Integration**: Host system integration

### Low Priority
1. **Load Testing**: High concurrency scenarios
2. **Edge Cases**: Unusual input combinations
3. **Documentation**: Code examples and documentation accuracy
4. **Advanced Features**: Complex configuration scenarios

This comprehensive testing strategy ensures the MCPB is production-ready and compatible with the MCPB ecosystem while maintaining high quality and reliability standards.