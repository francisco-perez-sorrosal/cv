# CI/CD Documentation: Automated Branch Management

## Introduction

This repository implements an automated CI/CD system designed to maintain synchronization between the `main` and `mcp` branches. The system addresses the unique challenge of keeping two functionally different branches in sync:

- **`main` branch**: Contains the core LaTeX CV files and minimal repository structure
- **`mcp` branch**: Contains a comprehensive Python-based MCP (Model Context Protocol) server implementation with additional tooling, dependencies, and infrastructure

The automated workflows ensure that updates to the foundational CV content in `main` are automatically propagated to the `mcp` branch while preserving the additional functionality and files unique to the MCP implementation.

## TL;DR - Workflow Summary

| Workflow | Trigger | Purpose | Interaction |
|----------|---------|---------|-------------|
| **Auto Rebase MCP** | Push to `main`, Manual | Automatically rebase `mcp` onto `main` with intelligent conflict resolution | Creates issues for **Status Check** to monitor |
| **Rebase Status Check** | Daily schedule, Manual | Monitor branch synchronization and track rebase health | Responds to issues created by **Auto Rebase** |

### Quick Functionality Overview

1. **Auto Rebase MCP Branch** (`auto-rebase-mcp.yml`)
   - 🔄 Automatically rebases `mcp` branch when `main` is updated
   - 🧠 Intelligent conflict resolution for common scenarios
   - 🔧 Creates detailed issues when manual intervention is needed
   - 📋 Comprehensive backup and rollback capabilities

2. **Rebase Status Check** (`rebase-status-check.yml`)
   - 📊 Daily health checks of branch synchronization
   - 🚨 Alerts when branches drift out of sync
   - 📝 Tracks and manages rebase-related issues
   - 🔄 Provides actionable recommendations

### Workflow Interactions

- **Auto Rebase** creates conflict issues → **Status Check** monitors and manages them
- **Status Check** detects sync issues → Can trigger **Auto Rebase** manually
- Both workflows share issue labels and tracking for unified management
- Backup branches created by **Auto Rebase** are cleaned up automatically

---

## Detailed Workflow Documentation

### 1. Auto Rebase MCP Branch Workflow

**File:** `.github/workflows/auto-rebase-mcp.yml`

#### Purpose
Automatically maintains the `mcp` branch as an up-to-date version of `main` with additional MCP-specific functionality, handling the complex task of merging two divergent branches with intelligent conflict resolution.

#### Triggers
- **Automatic**: Every push to the `main` branch
- **Manual**: Workflow dispatch with optional parameters:
  - `force_rebase`: Force rebase even when branches appear synchronized
  - `dry_run`: Validate rebase process without making changes

#### Key Features

##### 🔍 **Smart Change Detection**
```yaml
# Only performs rebase when actually needed
- Compares merge-base with main branch HEAD
- Shows exactly which new commits would be applied
- Skips unnecessary operations when branches are in sync
```

##### 🛡️ **Comprehensive Backup Strategy**
- Creates timestamped backup branches before any rebase attempt
- Automatic cleanup of old backup branches (keeps last 5)
- Full rollback capabilities in case of critical failures

##### 🧠 **Intelligent Conflict Resolution**
The workflow implements a multi-stage conflict resolution approach:

**Stage 1: Automatic Resolution**
```bash
# Uses git rebase with strategy options
git rebase --strategy-option=ours origin/main
```
- Prefers MCP branch changes by default
- Handles most straightforward conflicts automatically

**Stage 2: Advanced Pattern-Based Resolution**
- **.gitignore files**: Intelligently merges both versions, removing duplicates
- **LaTeX/PDF files**: Preserves main branch versions (main is authoritative for document changes)
- **CLAUDE.md**: Keeps comprehensive MCP version while logging the decision

**Stage 3: Manual Intervention**
- Creates detailed GitHub issues with step-by-step resolution instructions
- Provides multiple resolution paths (command line, GitHub web interface)
- Includes context about specific conflicted files and recommended strategies

##### ✅ **Validation and Safety Checks**
```yaml
# Post-rebase validation
- name: Validate rebased branch
  # Ensures critical files are preserved
  # Checks repository integrity
  # Validates expected file structure
```

##### 📊 **Comprehensive Reporting**
- Success notifications with detailed rebase information
- Failure issues with actionable resolution steps
- Workflow summaries with backup branch information
- Commit comments for traceability

#### Workflow Steps Deep Dive

1. **Repository Setup**
   - Checks out with full history (`fetch-depth: 0`)
   - Configures git with bot credentials
   - Sets up concurrency controls to prevent overlapping rebases

2. **Change Analysis**
   - Calculates merge base between branches
   - Determines if rebase is actually needed
   - Lists new commits that would be applied

3. **Backup Creation**
   - Creates timestamped backup branch
   - Pushes backup to remote for safety
   - Records backup branch name for reference

4. **Rebase Execution**
   ```bash
   # Three-phase rebase approach
   Phase 1: Automatic (--strategy-option=ours)
   Phase 2: Pattern-based conflict resolution  
   Phase 3: Manual intervention (issue creation)
   ```

5. **Validation**
   - Ensures essential files are preserved
   - Validates branch integrity
   - Confirms expected repository structure

6. **Finalization**
   - Pushes rebased branch with force-with-lease
   - Creates success notifications
   - Cleans up temporary branches
   - Manages backup branch lifecycle

#### Error Handling and Recovery

The workflow implements comprehensive error handling:

- **Conflict Detection**: Identifies and categorizes different types of conflicts
- **Automatic Recovery**: Attempts multiple resolution strategies before failing
- **Safe Rollback**: Can restore from backup branches if needed
- **Issue Creation**: Provides detailed manual resolution instructions
- **Cleanup**: Ensures no temporary state is left behind

#### Configuration Options

Key environment variables and configuration:
```yaml
env:
  TARGET_BRANCH: mcp    # Branch to be rebased
  BASE_BRANCH: main     # Branch to rebase onto
```

### 2. Rebase Status Check Workflow

**File:** `.github/workflows/rebase-status-check.yml`

#### Purpose
Provides continuous monitoring of branch synchronization health, proactive alerting for drift issues, and centralized management of rebase-related tracking.

#### Triggers
- **Scheduled**: Daily at 6:00 AM UTC
- **Manual**: Workflow dispatch with optional notification control

#### Key Features

##### 📊 **Comprehensive Branch Analysis**
```bash
# Multi-metric synchronization assessment
- Merge base calculation
- Commits ahead/behind analysis  
- Divergence detection
- Last workflow status tracking
```

##### 🚨 **Proactive Issue Management**
- **Smart Issue Tracking**: Creates/updates a single tracking issue rather than spam
- **Automatic Resolution**: Closes issues when branches are synchronized
- **Priority Classification**: Labels issues based on urgency and type

##### 📝 **Detailed Status Reporting**
Each status check generates comprehensive reports including:
- Current commit information for both branches
- Synchronization status with specific metrics
- List of new commits in main (if behind)
- Recommendations for next steps
- Links to relevant workflows and actions

##### 🔧 **Integration with Auto Rebase**
- Monitors success/failure of automatic rebase attempts
- Tracks open conflict issues
- Provides direct links to trigger manual rebases
- Manages the lifecycle of rebase-related issues

#### Workflow Logic Flow

1. **Branch Status Assessment**
   ```bash
   # Calculates comprehensive sync metrics
   COMMITS_BEHIND=$(git rev-list --count $MERGE_BASE..$MAIN_HEAD)
   COMMITS_AHEAD=$(git rev-list --count $MERGE_BASE..$MCP_HEAD)
   ```

2. **Conflict Issue Analysis**
   - Scans for open rebase-conflict issues
   - Counts and categorizes pending manual interventions
   - Assesses overall rebase health

3. **Report Generation**
   - Creates markdown-formatted status reports
   - Includes actionable recommendations
   - Provides direct workflow links for easy access

4. **Issue Management Logic**
   ```yaml
   # Smart issue lifecycle management
   Needs Attention + No Existing Issue → Create New Issue
   Needs Attention + Existing Issue → Update Issue  
   No Attention Needed + Existing Issue → Close Issue
   No Attention Needed + No Issue → No Action
   ```

#### Status Categories and Actions

| Status | Description | Automated Action |
|--------|-------------|------------------|
| `up_to_date` | Branches synchronized | Close tracking issues |
| `behind` | MCP behind main | Create/update alert issue |
| `diverged` | Branches have diverged | Create high-priority issue |

#### Report Structure

Each status report includes:

**Current Status Section**
- Branch heads with latest commit info
- Sync status classification
- Commit count metrics

**Change Analysis** (when behind)
- List of new commits in main
- Impact assessment
- Recommended actions

**Issue Summary** (when conflicts exist)
- Count of open rebase issues
- Links to specific problems
- Resolution guidance

**Recommendations Section**
- Specific next steps
- Workflow trigger links
- Priority assessments

### Configuration and Customization

#### Environment Variables
Both workflows use consistent environment variables:
```yaml
env:
  TARGET_BRANCH: mcp    # The branch that gets rebased
  BASE_BRANCH: main     # The base branch for rebasing
```

#### Permission Requirements
```yaml
permissions:
  contents: write        # For git operations
  actions: write         # For workflow management  
  issues: write          # For issue creation/management
  pull-requests: write   # For PR-based resolution
```

#### Label Management
The system uses consistent labels across workflows:
- `automation`: All automated actions
- `rebase-conflict`: Manual intervention needed
- `rebase-status`: Status tracking issues
- `help wanted`: Community assistance welcome
- `high-priority`: Urgent attention required

### Best Practices and Recommendations

#### For Repository Maintainers

1. **Monitor Issues Regularly**
   - Check for `rebase-conflict` labels weekly
   - Prioritize `high-priority` rebase issues
   - Review automated status reports

2. **Understand Conflict Patterns**
   - LaTeX files: Keep main branch version (main is authoritative for document changes)
   - README.md: Keep main branch version (main is authoritative for documentation)
   - CLAUDE.md: Keep MCP branch version (MCP has comprehensive documentation)
   - Configuration: Combine intelligently

3. **Use Backup Branches**
   - Backup branches are created before every rebase
   - Use them for quick rollbacks if needed
   - Only the latest backup is kept (previous ones automatically removed)

#### For Contributors

1. **Contributing to Main Branch**
   - Be aware that changes trigger automatic rebasing
   - Consider impact on MCP branch functionality
   - Review any generated conflict issues

2. **Contributing to MCP Branch**
   - Understand that branch gets rebased onto main
   - Don't be surprised by apparent "lost" commits (they're rebased)
   - Check backup branches if you need to recover work

#### For Emergency Situations

**Quick Rollback Procedure:**
```bash
# Find the latest backup branch
git branch -r | grep mcp-backup | tail -1

# Reset MCP branch to backup
git checkout mcp
git reset --hard origin/mcp-backup-YYYYMMDD-HHMMSS
git push --force-with-lease origin mcp
```

**Manual Rebase Process:**
```bash
# When automatic rebase fails
git checkout mcp
git fetch origin main
git rebase origin/main
# Resolve conflicts manually
git add <resolved-files>
git rebase --continue
git push --force-with-lease origin mcp
```

### Monitoring and Maintenance

#### Key Metrics to Track
- Rebase success rate
- Time between main commits and MCP updates
- Frequency of manual interventions needed
- Types of conflicts most commonly encountered

#### Regular Maintenance Tasks
- Review and close resolved rebase issues
- Update conflict resolution strategies based on patterns
- Adjust scheduling if repository activity changes
- Update documentation as workflows evolve

#### Troubleshooting Common Issues

**Issue**: Workflows not triggering
- Check branch protection rules
- Verify GitHub Actions is enabled
- Confirm workflow file syntax

**Issue**: Permissions errors
- Review repository permissions
- Check if workflows need additional scopes
- Verify token permissions in settings

**Issue**: Frequent conflicts
- Review branching strategy
- Consider adjusting conflict resolution preferences
- Add custom resolution logic for specific file patterns

### Future Enhancements

Potential improvements for the CI/CD system:

1. **Advanced Conflict Resolution**
   - Machine learning-based conflict resolution
   - Custom merge drivers for specific file types
   - Integration with external diff tools

2. **Enhanced Monitoring**
   - Slack/Teams notifications
   - Dashboard for rebase health metrics
   - Historical trend analysis

3. **Testing Integration**
   - Run tests before finalizing rebases  
   - Validate MCP server functionality post-rebase
   - Automated quality checks

4. **Performance Optimization**
   - Shallow clones for faster operations
   - Parallel processing where possible
   - Caching strategies for repeated operations

This CI/CD system provides a robust, automated solution for maintaining branch synchronization while handling the complexity of two divergent branches with different purposes and file structures.

## Recent Changes

### Transport and Project Script Updates

- **SSE Transport Deprecation**: The MCP server no longer supports `sse` transport. Use `streamable-http` instead.
- **Project Script Fix**: The `pyproject.toml` now correctly defines `cv-mcp-server = "cv_mcp_server.main:main"` entry point.
- **Enhanced Pixi Commands**: The server can now be launched using `pixi run cv-mcp-server` after proper installation.

## How the Rebase Status Check Provides Tracking and Recommendations

The Rebase Status Check workflow delivers tracking and recommendation information through **GitHub Issues** as a centralized dashboard system. This section explains the comprehensive mechanism for information delivery and user interaction.

### 📊 Information Delivery Mechanism

#### 1. **Smart Issue Management System**
The workflow uses GitHub Issues as a persistent dashboard that:
- **Creates** a single tracking issue when branches drift out of sync
- **Updates** the existing issue with new status information 
- **Closes** the issue automatically when branches are synchronized
- **Prevents spam** by maintaining one issue instead of creating multiple

#### 2. **Issue Lifecycle Logic**
```yaml
# The workflow follows this decision tree:
Needs Attention + No Existing Issue → Create New Issue
Needs Attention + Existing Issue → Update Issue + Add Comment  
No Attention Needed + Existing Issue → Close Issue + Add Closure Comment
No Attention Needed + No Issue → No Action (silent)
```

### 📝 What Information Is Provided

#### **Issue Title Format:**
```
🔄 Branch Synchronization Status - MCP behind Main
```

#### **Detailed Status Report Content:**
The issue body contains a comprehensive markdown report:

```markdown
# 🔄 Branch Synchronization Status Report

**Generated:** 2025-08-13 14:30:15 UTC

## Current Status
- **Main Branch:** `main` (a1b2c3d - Add new CV section)
- **MCP Branch:** `mcp` (x9y8z7w - Update MCP server config)
- **Sync Status:** behind
- **Commits Behind:** 3
- **Commits Ahead:** 7

### Recent Commits in Main (not in MCP)
```
a1b2c3d Add new CV section
b2c3d4e Fix LaTeX formatting issue
c3d4e5f Update contact information
```

## ⚠️ Open Rebase Issues
There are currently 2 open rebase conflict issues that need attention.

## Recommendations
- 🔄 Consider triggering a manual rebase using the [Auto Rebase workflow](../../actions/workflows/auto-rebase-mcp.yml)
- 📋 Review the commits listed above to understand what changes will be applied
- 🔧 Resolve open rebase conflict issues before proceeding with new rebases

---

**Next Check:** Scheduled for tomorrow at 06:00 UTC  
**Manual Trigger:** [Run Status Check](../../actions/workflows/rebase-status-check.yml)  
**Trigger Rebase:** [Run Auto Rebase](../../actions/workflows/auto-rebase-mcp.yml)

*Auto-generated by rebase status check workflow*
```

### 🔄 How Users Access This Information

#### **Primary Access Points:**

1. **GitHub Issues Tab**
   - Look for issues labeled: `rebase-status`, `automation`
   - Issues marked `attention-needed` require action
   - Issues marked `info` are just informational

2. **Issue Notifications**
   - GitHub sends notifications when issues are created/updated
   - Users subscribed to the repository get email/in-app notifications
   - Issue comments provide status change alerts

3. **Direct Links in Issues**
   - **Clickable workflow links** to trigger actions immediately
   - **Deep links** to specific workflow runs for context
   - **Branch comparison links** to see differences visually

#### **User Workflow:**
```
Daily at 6 AM UTC → Status Check Runs → Issue Created/Updated → User Notified → User Reviews Issue → User Takes Action
```

### 🚨 Alert Prioritization

The system uses **GitHub Labels** for prioritization:

| Label | Meaning | User Action |
|-------|---------|-------------|
| `attention-needed` | Branches out of sync | Review and potentially trigger rebase |
| `rebase-conflict` | Manual intervention needed | Resolve conflicts immediately |
| `high-priority` | Critical sync issues | Urgent attention required |
| `info` | Status information only | No immediate action needed |

### 💡 Interactive Elements

#### **Direct Action Links:**
Users can click directly from the issue to:
- **Trigger Auto Rebase**: `[Run Auto Rebase](../../actions/workflows/auto-rebase-mcp.yml)`
- **Run Status Check**: `[Run Status Check](../../actions/workflows/rebase-status-check.yml)`
- **View Workflow History**: Links to specific workflow runs

#### **Contextual Information:**
- **Commit lists**: Shows exactly what changes will be applied
- **File change summaries**: Indicates what types of files have changed
- **Conflict predictions**: Based on historical patterns

### 📱 Notification Channels

#### **Built-in GitHub Notifications:**
- **Email notifications** when issues are created/updated
- **In-app notifications** in GitHub interface
- **Mobile push notifications** via GitHub mobile app

#### **Issue Comments for Updates:**
When status changes, the workflow adds comments like:
```markdown
🔄 **Status Update - 2025-08-13**

Branch sync status has been updated. Check the issue description for current details.
```

Or for resolution:
```markdown
✅ **Issue Resolved**

Branches are now synchronized. Closing this status tracking issue.
```

### 🔍 Example User Experience

**Day 1**: User pushes to `main` branch  
**Day 2**: Status check runs, creates issue: *"MCP is 1 commit behind main"*  
**Day 3**: Auto-rebase runs successfully, status check closes the issue  
**Day 4**: No issue exists (branches in sync)  
**Day 5**: User pushes complex changes, auto-rebase fails with conflicts  
**Day 6**: Status check updates issue with conflict details and resolution steps  

### 🎯 Key Benefits of This Approach

1. **Centralized Dashboard**: Single place to check branch health
2. **Persistent History**: Issues maintain history of sync problems
3. **Actionable Information**: Direct links to take corrective action
4. **Automatic Cleanup**: Issues auto-close when problems resolve
5. **Native Integration**: Uses GitHub's built-in notification system
6. **Mobile Friendly**: Accessible from GitHub mobile app

This system transforms the abstract concept of "branch synchronization status" into concrete, actionable GitHub Issues that users naturally interact with as part of their development workflow.