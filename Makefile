# Makefile for building and installing distributable packages

DIST_DIR   ?= dist
DIST_MCPB   = $(DIST_DIR)/mcpb
DIST_WHEEL  = $(DIST_DIR)/wheel
DIST_SKILL  = $(DIST_DIR)/skill

SKILLS = cv-analyst cv-tailoring

CLAUDE_DESKTOP_CONFIG = $(HOME)/Library/Application Support/Claude/claude_desktop_config.json
MCP_SERVER_KEY        = fps_cv_mcp
REMOTE_MCP_CONFIG     = config/cv_mcp.json

.PHONY: all build-mcpb build-wheel build-skill \
        install-claude-desktop install-claude-code install-skills \
        clean

all: build-wheel build-mcpb

# --- Build targets ---

build-wheel:
	DIST_WHEEL=$(DIST_WHEEL) pixi run -e dev python-bundle

# Build process: update deps -> create lib directory -> create MCPB bundle
#
# lib/ contains native binary extensions (.so files for pydantic_core, pyyaml…)
# that are ABI-locked to the Python minor version used at build time. The
# wheels downloaded from PyPI are tagged with that ABI (e.g. cp313), so the
# bundle is loadable by ANY Python 3.13 interpreter on the user's machine
# (Homebrew, pyenv, conda-forge — they all share the cp313 ABI).
#
# We use pixi's dev env Python for the build (reproducible via pixi.lock).
# At runtime, start_mcpb.sh reads lib/.python-version and locates the
# matching python3.X on the host. Override the build Python if needed:
#   make build-mcpb BUNDLE_PIXI_FEATURE=otherenv
build-mcpb:
	pixi install
	pixi run -e dev update-mcpb-deps
	pixi run -e dev mcp-bundle
	@ls lib/pydantic_core/*.so 2>/dev/null | sed -n 's/.*cpython-\([0-9]\)\([0-9][0-9]*\).*/\1.\2/p' | head -1 > lib/.python-version
	@test -s lib/.python-version || (echo "ERROR: could not detect cpython ABI from lib/pydantic_core/*.so" && exit 1)
	@echo "Recorded lib/.python-version: $$(cat lib/.python-version) (derived from .so ABI tag)"
	DIST_MCPB=$(DIST_MCPB) pixi run pack

# Package skills as zips for claude.ai (Settings > Features > Add Skill)
build-skill:
	mkdir -p $(DIST_SKILL)
	@for skill in $(SKILLS); do \
		cd skills/$$skill && zip -r ../../$(DIST_SKILL)/$$skill.zip SKILL.md references/ && cd ../..; \
	done

# --- Install targets ---

# Install for Claude Desktop
# Usage: make install-claude-desktop                    # local (default): build MCPB + skill
#        make install-claude-desktop MCP_TARGET=remote   # remote: build skill + inject MCP config
MCP_TARGET ?= local
install-claude-desktop:
ifeq ($(MCP_TARGET),local)
	$(MAKE) build-mcpb build-skill
	@echo ""
	@echo "Packages built. Install manually in Claude Desktop:"
	@echo ""
	@echo "  MCP Server:  Open Settings > Extensions > Add, install $(DIST_MCPB)/*.mcpb"
	@echo "  Skills:      Open Settings > Features > Add Skill, upload each zip from $(DIST_SKILL)/"
	@echo ""
else ifeq ($(MCP_TARGET),remote)
	$(MAKE) build-skill
	@if [ ! -f "$(CLAUDE_DESKTOP_CONFIG)" ]; then \
		echo "Error: Claude Desktop config not found at $(CLAUDE_DESKTOP_CONFIG)"; \
		exit 1; \
	fi
	@if jq -e '.mcpServers.$(MCP_SERVER_KEY)' "$(CLAUDE_DESKTOP_CONFIG)" > /dev/null 2>&1; then \
		echo "MCP server: $(MCP_SERVER_KEY) already present in Claude Desktop config — skipping"; \
	else \
		jq --argjson cfg "$$(cat $(REMOTE_MCP_CONFIG))" \
			'.mcpServers.$(MCP_SERVER_KEY) = $$cfg' "$(CLAUDE_DESKTOP_CONFIG)" > "$(CLAUDE_DESKTOP_CONFIG).tmp" \
			&& mv "$(CLAUDE_DESKTOP_CONFIG).tmp" "$(CLAUDE_DESKTOP_CONFIG)"; \
		echo "MCP server: $(MCP_SERVER_KEY) injected into Claude Desktop config"; \
	fi
	@echo ""
	@echo "Skills built. Install manually in Claude Desktop:"
	@echo "  Skills: Open Settings > Features > Add Skill, upload each zip from $(DIST_SKILL)/"
	@echo ""
endif

# Install Claude Code plugin
# Usage: make install-claude-code                      # local (default): local plugin + local MCP
#        make install-claude-code MCP_TARGET=remote     # marketplace plugin (remote MCP built-in)
install-claude-code:
ifeq ($(MCP_TARGET),local)
	@jq --argjson cfg "$$(jq '.mcpServers.$(MCP_SERVER_KEY)' .claude-plugin/mcp-local.json)" \
		'.mcpServers.$(MCP_SERVER_KEY) = $$cfg' .mcp.json > .mcp.json.tmp \
		&& mv .mcp.json.tmp .mcp.json
	@echo "MCP server: local (stdio via pixi) -> .mcp.json"
	claude plugin install --scope user .
	@echo "Plugin: installed from local directory"
else ifeq ($(MCP_TARGET),remote)
	claude plugin marketplace add francisco-perez-sorrosal/bit-agora
	claude plugin install --scope user cv
	@echo "Plugin: cv installed from bit-agora marketplace"
endif

# --- Clean ---

clean:
	pixi run clean-bundles
	rm -rf $(DIST_DIR)/
