# Makefile for building and installing distributable packages

DIST_DIR   ?= dist
DIST_MCPB   = $(DIST_DIR)/mcpb
DIST_WHEEL  = $(DIST_DIR)/wheel
DIST_SKILL  = $(DIST_DIR)/skill

# Skills API (beta) — requires ANTHROPIC_API_KEY env var
SKILLS_API_URL     = https://api.anthropic.com/v1/skills
SKILLS_API_VERSION = 2023-06-01
SKILLS_API_BETA    = skills-2025-10-02
SKILL_NAME         = cv-analyst
SKILL_TITLE        = CV Analyst

.PHONY: all build-mcpb build-wheel build-skill \
        install-claude-desktop install-mcp-desktop install-skill-api \
        clean

all: build-wheel build-mcpb

# --- Build targets ---

build-wheel:
	DIST_WHEEL=$(DIST_WHEEL) pixi run -e dev python-bundle

# Build process: update deps -> create lib directory -> create MCPB bundle
build-mcpb:
	pixi install
	pixi run -e dev update-mcpb-deps
	pixi run -e dev mcp-bundle
	DIST_MCPB=$(DIST_MCPB) pixi run pack

# Package the cv-analyst skill as a zip for claude.ai (Settings > Features)
build-skill:
	mkdir -p $(DIST_SKILL)
	cd skills/$(SKILL_NAME) && zip -r ../../$(DIST_SKILL)/$(SKILL_NAME).zip SKILL.md references/

# --- Install targets ---

# Install MCP server locally + upload skill to API workspace
install-claude-desktop: install-mcp-desktop install-skill-api

# Register the MCP server in Claude Desktop config
install-mcp-desktop:
	./install_claude_mcp.sh desktop

# Upload the skill zip via the Anthropic Skills API (workspace-wide)
# Requires: ANTHROPIC_API_KEY environment variable
install-skill-api: build-skill
ifndef ANTHROPIC_API_KEY
	$(error ANTHROPIC_API_KEY is not set. Export it before running this target)
endif
	@echo "Uploading skill '$(SKILL_TITLE)' via Skills API..."
	@curl -sf -X POST "$(SKILLS_API_URL)" \
		-H "x-api-key: $(ANTHROPIC_API_KEY)" \
		-H "anthropic-version: $(SKILLS_API_VERSION)" \
		-H "anthropic-beta: $(SKILLS_API_BETA)" \
		-F "display_title=$(SKILL_TITLE)" \
		-F "files[]=@$(DIST_SKILL)/$(SKILL_NAME).zip;filename=skill.zip" \
	| jq '{ id: .id, title: .display_title, version: .latest_version }'
	@echo "Skill uploaded to API workspace. Use skill_id in Messages API container.skills."
	@echo "Note: For claude.ai web UI, upload $(DIST_SKILL)/$(SKILL_NAME).zip manually via Settings > Features."

# --- Clean ---

clean:
	pixi run clean-bundles
	rm -rf $(DIST_DIR)/
