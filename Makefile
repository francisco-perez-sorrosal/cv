# Makefile for building the MCPB package for Claude Extensions

.PHONY: all build-mcpb build-wheel clean

all: build-wheel build-mcpb

build-wheel:
	pixi run -e dev python-bundle

# Build process: update deps → create lib directory → create MCPB bundle
build-mcpb:
	pixi install
	pixi run -e dev update-mcpb-deps    # Update and export dependencies
	pixi run -e dev mcp-bundle          # Install deps to lib/ directory
	pixi run pack                       # Creates MCPB bundle

clean:
	pixi run clean-bundles
