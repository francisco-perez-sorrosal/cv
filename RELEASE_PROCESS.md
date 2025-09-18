# Release Process for CV MCP Server

This document describes the automated release process for the CV MCP Server MCPB bundles.

## Quick Release

To create a new release, simply run:

```bash
./scripts/release.sh 0.0.1
```

This will handle everything automatically:
1. ✅ Update versions in `manifest.json` and `pyproject.toml`
2. ✅ Commit the version changes
3. ✅ Create and push a git tag (`v0.0.1`)
4. ✅ Trigger GitHub Actions to build and release the MCPB bundle

## Release Workflow

### 1. Automated GitHub Actions

When you push a tag (e.g., `v0.0.1`), the following happens automatically:

#### `release-mcpb.yml` workflow:
- ✅ Sets up Python 3.13 environment (Claude Desktop compatibility)
- ✅ Installs all required tools (pixi, uv, MCPB CLI)
- ✅ Updates manifest.json with the tag version
- ✅ Builds dependencies using Python 3.13
- ✅ Creates versioned MCPB bundle (`fps-cv-mcp-0.0.1.mcpb`)
- ✅ Creates GitHub release with detailed release notes
- ✅ Attaches MCPB bundle to the release
- ✅ Uploads bundle as build artifact (90-day retention)

#### `check-mcpb-creation.yml` workflow:
- ✅ Runs on pull requests and pushes to `mcp` branch
- ✅ Validates manifest.json structure
- ✅ Tests MCP server startup
- ✅ Verifies MCPB bundle can be built successfully
- ✅ Validates bundle archive integrity

### 2. Release Artifacts

Each release includes:
- **MCPB Bundle**: `fps-cv-mcp-{version}.mcpb`
- **Python Version**: 3.13 compatible
- **Architecture**: ARM64 (macOS Apple Silicon)
- **Size**: ~30MB compressed, ~70MB unpacked
- **Dependencies**: All bundled in `lib/` directory

### 3. Version Management

The release process maintains version consistency across:
- `manifest.json` - MCPB bundle metadata
- `pyproject.toml` - Python package metadata
- Git tags - Version control and release triggers

## Manual Release (Advanced)

If you need manual control over the release process:

### Step 1: Update Versions
```bash
# Edit manifest.json and pyproject.toml to update version fields
# Then commit the changes
git add manifest.json pyproject.toml
git commit -m "chore: bump version to 0.0.1"
```

### Step 2: Create Tag
```bash
git tag -a v0.0.1 -m "Release version 0.0.1"
git push origin mcp
git push origin v0.0.1
```

### Step 3: Monitor Workflow
- Check GitHub Actions: https://github.com/francisco-perez-sorrosal/cv/actions
- Verify release: https://github.com/francisco-perez-sorrosal/cv/releases

## Testing Locally

Before creating a release, test the bundle locally:

```bash
# Build and test bundle
make build-mcpb

# Test the bundle
cd mcpb-package
unzip fps-cv-mcp-0.0.1.mcpb -d test/
cd test/
./start_mcpb.sh  # Should start without errors

# Clean up
cd ../../..
make clean
```

## Troubleshooting

### Common Issues

1. **Python Version Mismatch**
   - Ensure dependencies are built with Python 3.13
   - Check that `_pydantic_core.cpython-313-darwin.so` exists in bundle

2. **Missing Dependencies**
   - Run `pixi run update-mcpb-deps` to refresh requirements.txt
   - Verify all dependencies are in `lib/` directory

3. **Tag Already Exists**
   - Delete existing tag: `git tag -d v0.0.1 && git push origin :refs/tags/v0.0.1`
   - Or use a different version number

4. **Workflow Failures**
   - Check GitHub Actions logs for detailed error messages
   - Ensure all required secrets are configured (GITHUB_TOKEN is automatic)

### Debug Commands

```bash
# Test version extraction
python3 -c "import json; print(json.load(open('manifest.json'))['version'])"

# Test bundle filename generation
python3 -c "import json; print(f\"{json.load(open('manifest.json'))['name']}-{json.load(open('manifest.json'))['version']}.mcpb\")"

# Test dependency installation
python3.13 -m pip install -r requirements.txt --target test-lib/
```

## Release Checklist

Before creating a release:

- [ ] All changes committed to `mcp` branch
- [ ] Working directory is clean (`git status`)
- [ ] Tests pass locally (`pixi run start` works)
- [ ] MCPB bundle builds successfully (`make build-mcpb`)
- [ ] Version number follows semantic versioning
- [ ] Release notes are meaningful

After release:
- [ ] GitHub Actions workflow completed successfully
- [ ] Release appears on GitHub releases page
- [ ] MCPB bundle is attached to release
- [ ] Bundle size is reasonable (~30MB)
- [ ] Test installation in Claude Desktop
