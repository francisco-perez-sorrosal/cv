I want to build this project containing a python MCP server as a MCP Bundle, abbreviated as "MCPB". Please follow these steps:

1. Read the specifications thoroughly:

- https://github.com/anthropics/mcpb/blob/main/README.md - MCPB architecture overview, capabilities, and integration patterns
- https://github.com/anthropics/mcpb/blob/main/MANIFEST.md - Complete bundle manifest structure and field definitions
- https://github.com/anthropics/mcpb/tree/main/examples - Reference implementations including a "Hello World" example

2. Create a proper bundle structure:

- Assume the project root contains already an MCP server implementation in this case in Python
- The source code of the MCP server is in a python package under the src/ directory in the project root
- Generate a valid manifest.json following the MANIFEST.md spec

3. Ensure that project follows the best development practices below (but don't implement them, write a report in a file named MCPB_DEV_PRACTICES_IMPROVEMENTS.md):

- Check the current implementation supports proper MCP protocol communications via stdio, and streamable-http transports
- Check that tools have been structured with clear schemas, validation, and consistent JSON responses
- Make use of the fact that this bundle will be running locally and remotely
- Check that there are appropriate logging and debugging capabilities
- Include proper documentation and setup instructions

4. Check the test considerations below (but don't implement them. Instead write a report in a file named MCPB_TEST_CONSIDERATIONS.md):

- Validate that all tool calls return properly structured responses
- Verify manifest loads correctly and host integration works
- Check that the current code is production-ready that can be immediately tested. Focus on defensive programming, clear error messages, and following the exact MCPB specifications to ensure compatibility with the ecosystem.
