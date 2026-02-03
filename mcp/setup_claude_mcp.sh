#!/bin/bash
# =============================================================================
# OpenHEXA Claude MCP Setup Script
# =============================================================================
# This script configures Claude CLI with OpenHEXA MCP servers in a JupyterHub
# notebook environment. It automatically detects workspace credentials,
# fetches MCP servers from GitHub, and sets up the necessary configuration.
#
# Usage: source setup_claude_mcp.sh
#        or: ./setup_claude_mcp.sh
#
# Prerequisites:
# - Running inside a JupyterHub notebook with OpenHEXA workspace
# - Node.js/npm available (for Claude CLI)
# - git available (for cloning MCP servers)
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# MCP Servers GitHub repository
MCP_REPO_URL="https://github.com/BLSQ/mcp_servers.git"
MCP_INSTALL_DIR="$HOME/.openhexa/mcp_servers"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  OpenHEXA Claude MCP Setup${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# =============================================================================
# Step 1: Detect environment and validate prerequisites
# =============================================================================
echo -e "${YELLOW}[1/8] Checking environment...${NC}"

# Detect where we're running (for debugging connectivity issues)
if [ -f "/.dockerenv" ] || grep -q docker /proc/1/cgroup 2>/dev/null; then
    echo "  Running inside Docker container"
    RUNNING_IN_DOCKER=true
else
    echo "  Running on host machine"
    RUNNING_IN_DOCKER=false
fi

# Check if we're in a JupyterHub environment with OpenHEXA credentials
if [ -z "$HEXA_SERVER_URL" ]; then
    echo -e "${RED}Error: HEXA_SERVER_URL not set.${NC}"
    echo "This script should be run inside a JupyterHub notebook with OpenHEXA workspace."
    echo ""
    echo "If running locally for testing, set these environment variables:"
    echo "  export HEXA_SERVER_URL=http://localhost:8001"
    echo "  export HEXA_WORKSPACE=your-workspace-slug"
    echo "  export HEXA_TOKEN=your-token"
    echo "  export WORKSPACE_DATABASE_URL=postgresql://user:pass@host:port/db"
    echo "  export WORKSPACE_DATABASE_DB_NAME=your-db-name"
    exit 1
fi

if [ -z "$HEXA_WORKSPACE" ]; then
    echo -e "${RED}Error: HEXA_WORKSPACE not set.${NC}"
    echo "Please ensure you're in a workspace notebook session."
    exit 1
fi

if [ -z "$HEXA_TOKEN" ]; then
    echo -e "${RED}Error: HEXA_TOKEN not set.${NC}"
    echo "Please ensure you're in an authenticated workspace notebook session."
    exit 1
fi

# Helper function to mask sensitive values (show first 3 and last 3 chars)
mask_secret() {
    local value="$1"
    local len=${#value}
    if [ $len -le 6 ]; then
        echo "*****"
    else
        echo "${value:0:3}*****${value: -3}"
    fi
}

echo -e "${GREEN}✓ Environment variables detected${NC}"
echo "  - HEXA_SERVER_URL: $HEXA_SERVER_URL"
echo "  - HEXA_WORKSPACE: $HEXA_WORKSPACE"
echo "  - HEXA_TOKEN: $(mask_secret "$HEXA_TOKEN")"

# Check for database credentials
if [ -z "$WORKSPACE_DATABASE_URL" ]; then
    echo -e "${YELLOW}Warning: WORKSPACE_DATABASE_URL not set. PostgreSQL MCP server will not be configured.${NC}"
    HAS_DB=false
    POSTGRES_CONN_STRING=""
else
    echo "  - WORKSPACE_DATABASE_URL: $(mask_secret "$WORKSPACE_DATABASE_URL")"
    echo "  - WORKSPACE_DATABASE_DB_NAME: ${WORKSPACE_DATABASE_DB_NAME:-unknown}"
    HAS_DB=true

    # Save original URL to detect if it was modified later
    ORIGINAL_WORKSPACE_DATABASE_URL="$WORKSPACE_DATABASE_URL"

    # The WORKSPACE_DATABASE_URL may contain a Docker service hostname (e.g., "test.db")
    # that may not be resolvable from all containers. We need to auto-detect and fix it.
    POSTGRES_CONN_STRING="$WORKSPACE_DATABASE_URL"

    # Extract components from the connection string
    # Format: postgresql://user:pass@hostname:port/dbname
    if [[ "$WORKSPACE_DATABASE_URL" =~ postgresql://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+) ]]; then
        DB_USER="${BASH_REMATCH[1]}"
        DB_PASS="${BASH_REMATCH[2]}"
        DB_HOST="${BASH_REMATCH[3]}"
        DB_PORT="${BASH_REMATCH[4]}"
        DB_NAME="${BASH_REMATCH[5]}"
        echo "  - Database host: $DB_HOST:$DB_PORT"

        # Function to test database connectivity
        test_db_connection() {
            local test_host="$1"
            local test_port="$2"
            local test_conn="postgresql://${DB_USER}:${DB_PASS}@${test_host}:${test_port}/${DB_NAME}"

            # Try to connect using Python (more reliable than nc/telnet)
            # Use environment variable to avoid shell escaping issues with passwords
            PGCONN="$test_conn" python3 -c "
import psycopg2
import sys
import os
try:
    conn = psycopg2.connect(os.environ['PGCONN'], connect_timeout=3)
    conn.close()
    sys.exit(0)
except Exception as e:
    # Print error for debugging (only visible if script is run with -x)
    print(f'Connection error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null
            return $?
        }

        # Test if the original connection works
        echo "  Testing database connection..."
        if test_db_connection "$DB_HOST" "$DB_PORT"; then
            echo -e "${GREEN}  ✓ Database connection successful${NC}"
        else
            echo -e "${YELLOW}  Original host '$DB_HOST' not reachable, trying alternatives...${NC}"

            # List of alternative hosts to try (in order of preference)
            # These are common Docker service names and network configurations
            ALTERNATIVE_HOSTS=(
                "db:5432"                        # OpenHEXA Docker Compose service (internal port)
                "db:$DB_PORT"                    # Same but with original port if different
                "postgres:5432"                  # Common PostgreSQL service name
                "localhost:5434"                 # Local development (external port mapping)
                "127.0.0.1:5434"                 # Same as localhost
                "host.docker.internal:5434"      # Docker Desktop host access with external port
                "172.17.0.1:5434"                # Docker bridge network with external port
            )

            DB_CONNECTED=false
            for alt in "${ALTERNATIVE_HOSTS[@]}"; do
                ALT_HOST="${alt%:*}"
                ALT_PORT="${alt#*:}"
                echo "    Trying $ALT_HOST:$ALT_PORT..."
                if test_db_connection "$ALT_HOST" "$ALT_PORT"; then
                    echo -e "${GREEN}    ✓ Connected via $ALT_HOST:$ALT_PORT${NC}"
                    POSTGRES_CONN_STRING="postgresql://${DB_USER}:${DB_PASS}@${ALT_HOST}:${ALT_PORT}/${DB_NAME}"
                    DB_CONNECTED=true
                    break
                fi
            done

            if [ "$DB_CONNECTED" = false ]; then
                echo -e "${RED}  ✗ Could not connect to database with any known host${NC}"
                echo "    The PostgreSQL MCP server may not work correctly."
                echo "    You can manually set OPENHEXA_DB_HOST_OVERRIDE before running this script."
            fi
        fi
    elif [[ "$WORKSPACE_DATABASE_URL" =~ @([^:/@]+)(:|/) ]]; then
        # Fallback for simpler connection string formats
        DB_HOST="${BASH_REMATCH[1]}"
        echo "  - Database host: $DB_HOST"
    fi

    if [ "$POSTGRES_CONN_STRING" != "$WORKSPACE_DATABASE_URL" ]; then
        echo "  - Using connection: $(mask_secret "$POSTGRES_CONN_STRING")"

        # Export the working database URL so Jupyter notebooks can use it
        export WORKSPACE_DATABASE_URL="$POSTGRES_CONN_STRING"
        echo "  - Updated WORKSPACE_DATABASE_URL to use working host"

        # Also add to shell profile for persistence across terminal sessions
        SHELL_PROFILE="$HOME/.bashrc"
        if [ -f "$HOME/.zshrc" ]; then
            SHELL_PROFILE="$HOME/.zshrc"
        fi

        # Remove any old WORKSPACE_DATABASE_URL override and add new one
        grep -v "^export WORKSPACE_DATABASE_URL=" "$SHELL_PROFILE" > "${SHELL_PROFILE}.tmp" 2>/dev/null || true
        mv "${SHELL_PROFILE}.tmp" "$SHELL_PROFILE" 2>/dev/null || true
        echo "export WORKSPACE_DATABASE_URL=\"$POSTGRES_CONN_STRING\"" >> "$SHELL_PROFILE"
        echo -e "${GREEN}  ✓ Added WORKSPACE_DATABASE_URL to $SHELL_PROFILE${NC}"
    fi
fi

echo ""

# =============================================================================
# Step 2: Clone/Update MCP servers from GitHub
# =============================================================================
echo -e "${YELLOW}[2/8] Fetching MCP servers from GitHub...${NC}"

# Create parent directory
mkdir -p "$(dirname "$MCP_INSTALL_DIR")"

if [ -d "$MCP_INSTALL_DIR/.git" ]; then
    # Directory exists and is a git repo - pull latest changes
    echo "  MCP servers directory exists, pulling latest changes..."
    cd "$MCP_INSTALL_DIR"

    # Get current branch or default to main/master
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
    echo "  Current branch: $CURRENT_BRANCH"

    # Show current commit before update
    OLD_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    echo "  Current commit: $OLD_COMMIT"

    # Fetch and pull - show output for debugging
    echo "  Fetching from origin..."
    if git fetch origin; then
        # Reset to origin to ensure we get the latest (handles diverged branches)
        echo "  Resetting to origin/$CURRENT_BRANCH..."
        if git reset --hard "origin/$CURRENT_BRANCH" 2>/dev/null || git reset --hard origin/main 2>/dev/null; then
            NEW_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
            if [ "$OLD_COMMIT" != "$NEW_COMMIT" ]; then
                echo -e "${GREEN}✓ Updated MCP servers: $OLD_COMMIT -> $NEW_COMMIT${NC}"
                # Show what files changed
                echo "  Changed files:"
                git diff --name-only "$OLD_COMMIT" HEAD 2>/dev/null | head -10 | sed 's/^/    - /'
            else
                echo -e "${GREEN}✓ MCP servers already up to date ($NEW_COMMIT)${NC}"
            fi
        else
            echo -e "${YELLOW}Warning: Could not reset to latest, using existing version${NC}"
        fi
    else
        echo -e "${YELLOW}Warning: Could not fetch from remote, using existing version${NC}"
    fi
    cd - > /dev/null
elif [ -d "$MCP_INSTALL_DIR" ]; then
    # Directory exists but is NOT a git repo - backup and re-clone
    echo -e "${YELLOW}  MCP servers directory exists but is not a git repo${NC}"
    echo "  Backing up and re-cloning..."
    mv "$MCP_INSTALL_DIR" "${MCP_INSTALL_DIR}.backup.$(date +%Y%m%d%H%M%S)"
    git clone "$MCP_REPO_URL" "$MCP_INSTALL_DIR"
    echo -e "${GREEN}✓ Cloned MCP servers to $MCP_INSTALL_DIR${NC}"
else
    # Directory doesn't exist - clone fresh
    echo "  Cloning MCP servers repository..."
    git clone "$MCP_REPO_URL" "$MCP_INSTALL_DIR"
    echo -e "${GREEN}✓ Cloned MCP servers to $MCP_INSTALL_DIR${NC}"
fi

# Verify the MCP server files exist
if [ ! -f "$MCP_INSTALL_DIR/openhexa_mcp_server.py" ]; then
    echo -e "${RED}Error: openhexa_mcp_server.py not found in repository${NC}"
    echo "  Expected location: $MCP_INSTALL_DIR/openhexa_mcp_server.py"
    echo "  Please check the repository structure at: $MCP_REPO_URL"
    exit 1
fi

if [ ! -f "$MCP_INSTALL_DIR/postgres_mcp_server.py" ]; then
    echo -e "${YELLOW}Warning: postgres_mcp_server.py not found - PostgreSQL MCP will not be available${NC}"
fi

if [ ! -f "$MCP_INSTALL_DIR/CLAUDE.md" ]; then
    echo -e "${YELLOW}Warning: CLAUDE.md not found in repository${NC}"
fi

echo ""

# =============================================================================
# Step 3: Create writable dashboards directory in workspace
# =============================================================================
echo -e "${YELLOW}[3/8] Setting up dashboards directory...${NC}"

# Detect workspace directory (JupyterHub uses /home/jovyan/workspace)
if [ -d "/home/jovyan/workspace" ]; then
    WORKSPACE_DIR="/home/jovyan/workspace"
elif [ -d "$HOME/workspace" ]; then
    WORKSPACE_DIR="$HOME/workspace"
else
    WORKSPACE_DIR="$HOME"
fi

DASHBOARDS_DIR="$WORKSPACE_DIR/dashboards"

# Create dashboards directory with proper permissions
if [ ! -d "$DASHBOARDS_DIR" ]; then
    echo "  Creating dashboards directory: $DASHBOARDS_DIR"
    if mkdir -p "$DASHBOARDS_DIR" 2>/dev/null; then
        chmod 755 "$DASHBOARDS_DIR" 2>/dev/null || true
        echo -e "${GREEN}✓ Created dashboards directory${NC}"
    else
        echo -e "${YELLOW}  Cannot create dashboards in workspace (permission denied)${NC}"
        echo ""
        echo -e "${YELLOW}  To fix workspace permissions, run this command on the host machine:${NC}"
        echo -e "    ${BLUE}sudo chown -R 1000:100 /data/${HEXA_WORKSPACE}*${NC}"
        echo ""
        # Try to create in home directory as fallback
        DASHBOARDS_DIR="$HOME/dashboards"
        mkdir -p "$DASHBOARDS_DIR"
        echo -e "${GREEN}✓ Created dashboards directory in home: $DASHBOARDS_DIR${NC}"
        echo -e "${YELLOW}  Note: Files in $DASHBOARDS_DIR won't be visible in OpenHEXA frontend${NC}"
    fi
else
    echo -e "${GREEN}✓ Dashboards directory already exists: $DASHBOARDS_DIR${NC}"
fi

# Ensure the directory is writable
if [ -w "$DASHBOARDS_DIR" ]; then
    echo "  Directory is writable"
else
    echo -e "${YELLOW}  Warning: Dashboards directory may not be writable${NC}"
    # Try to fix permissions
    chmod 755 "$DASHBOARDS_DIR" 2>/dev/null || true
fi

# Export for use in CLAUDE.md
export DASHBOARDS_DIR

echo ""

# =============================================================================
# Step 4: Check/Install Claude CLI
# =============================================================================
echo -e "${YELLOW}[4/8] Checking Claude CLI installation...${NC}"

# Set up npm global directory in user space to avoid permission issues
NPM_GLOBAL_DIR="$HOME/.npm-global"
if [ ! -d "$NPM_GLOBAL_DIR" ]; then
    echo "  Setting up npm global directory in user space..."
    mkdir -p "$NPM_GLOBAL_DIR"
    npm config set prefix "$NPM_GLOBAL_DIR"
fi

# Add npm global bin to PATH if not already there
if [[ ":$PATH:" != *":$NPM_GLOBAL_DIR/bin:"* ]]; then
    export PATH="$NPM_GLOBAL_DIR/bin:$PATH"
    # Also add to .bashrc for future sessions
    if ! grep -q "NPM_GLOBAL_DIR" "$HOME/.bashrc" 2>/dev/null; then
        echo "" >> "$HOME/.bashrc"
        echo "# npm global packages in user space" >> "$HOME/.bashrc"
        echo "export PATH=\"\$HOME/.npm-global/bin:\$PATH\"" >> "$HOME/.bashrc"
    fi
fi

# Check if npm is available first
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm not found. Please install Node.js/npm first.${NC}"
    echo "You can install it with: apt-get install nodejs npm"
    exit 1
fi

# Check Node.js version (Claude CLI requires v18+)
NODE_VERSION=$(node --version 2>/dev/null | sed 's/v//' | cut -d. -f1)
if [ -n "$NODE_VERSION" ] && [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}Error: Node.js v18+ is required. Current version: $(node --version)${NC}"
    echo "Please upgrade Node.js before continuing."
    exit 1
fi

if command -v claude &> /dev/null; then
    CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "unknown")
    echo "  Current Claude CLI version: $CLAUDE_VERSION"

    # Check if we should update (always update to ensure latest with MCP support)
    echo "  Checking for updates..."
    npm update -g @anthropic-ai/claude-code 2>/dev/null

    NEW_VERSION=$(claude --version 2>/dev/null || echo "unknown")
    if [ "$NEW_VERSION" != "$CLAUDE_VERSION" ]; then
        echo -e "${GREEN}✓ Updated Claude CLI: $CLAUDE_VERSION -> $NEW_VERSION${NC}"
    else
        echo -e "${GREEN}✓ Claude CLI is up to date: $CLAUDE_VERSION${NC}"
    fi
else
    echo "Claude CLI not found. Installing latest version..."

    # Install Claude CLI globally (to user's npm-global directory)
    echo "  Installing to $NPM_GLOBAL_DIR..."
    npm install -g @anthropic-ai/claude-code@latest

    if command -v claude &> /dev/null; then
        CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "unknown")
        echo -e "${GREEN}✓ Claude CLI installed successfully: $CLAUDE_VERSION${NC}"
    else
        echo -e "${RED}Error: Claude CLI installation failed${NC}"
        echo "Try running: source ~/.bashrc && claude --version"
        exit 1
    fi
fi

# Verify MCP support is available
echo "  Verifying MCP support..."
if claude mcp list &>/dev/null; then
    echo -e "${GREEN}✓ MCP support is available${NC}"
else
    echo -e "${YELLOW}Warning: MCP commands may not be fully available yet${NC}"
fi

echo ""

# =============================================================================
# Step 4: Create MCP .env file
# =============================================================================
echo -e "${YELLOW}[5/8] Creating MCP environment file...${NC}"

MCP_ENV_FILE="$MCP_INSTALL_DIR/.env"

cat > "$MCP_ENV_FILE" << EOF
# OpenHEXA MCP Server Configuration
# Auto-generated by setup_claude_mcp.sh on $(date)
# Workspace: $HEXA_WORKSPACE

# OpenHEXA API Configuration
HEXA_SERVER_URL=$HEXA_SERVER_URL
HEXA_TOKEN=$HEXA_TOKEN

# Workspace Information (used by CLAUDE.md for dashboard building)
OH_WORKSPACE=$HEXA_WORKSPACE
HEXA_DB=${WORKSPACE_DATABASE_DB_NAME:-}

# PostgreSQL Connection (for postgres_mcp_server.py)
POSTGRES_CONNECTION_STRING=${WORKSPACE_DATABASE_URL:-}
EOF

echo -e "${GREEN}✓ Created $MCP_ENV_FILE${NC}"
echo ""

# =============================================================================
# Step 5: Ensure Python dependencies are installed
# =============================================================================
echo -e "${YELLOW}[6/8] Checking Python dependencies...${NC}"

# Check if required packages are installed
MISSING_PACKAGES=""

python3 -c "import fastmcp" 2>/dev/null || MISSING_PACKAGES="$MISSING_PACKAGES fastmcp"
python3 -c "import psycopg2" 2>/dev/null || MISSING_PACKAGES="$MISSING_PACKAGES psycopg2-binary"
python3 -c "import requests" 2>/dev/null || MISSING_PACKAGES="$MISSING_PACKAGES requests"
python3 -c "import dotenv" 2>/dev/null || MISSING_PACKAGES="$MISSING_PACKAGES python-dotenv"

if [ -n "$MISSING_PACKAGES" ]; then
    echo "Installing missing packages:$MISSING_PACKAGES"
    pip install $MISSING_PACKAGES --quiet
    echo -e "${GREEN}✓ Installed Python dependencies${NC}"
else
    echo -e "${GREEN}✓ All Python dependencies already installed${NC}"
fi

# Check if openhexa-sdk is installed (for openhexa_mcp_server.py)
if ! python3 -c "from openhexa.sdk.client import openhexa" 2>/dev/null; then
    echo "Installing openhexa-sdk..."
    pip install openhexa-sdk --quiet
    echo -e "${GREEN}✓ Installed openhexa-sdk${NC}"
fi

echo ""

# =============================================================================
# Step 6: Configure Claude settings with CLAUDE.md
# =============================================================================
echo -e "${YELLOW}[7/8] Configuring Claude settings...${NC}"

# Create Claude config directories
CLAUDE_CONFIG_DIR="$HOME/.claude"
mkdir -p "$CLAUDE_CONFIG_DIR"

# Try to create project-level .claude in current directory
# Fall back to home directory if permission denied
WORKSPACE_CLAUDE_DIR="$(pwd)/.claude"
if mkdir -p "$WORKSPACE_CLAUDE_DIR" 2>/dev/null; then
    echo "  Using project-level config: $WORKSPACE_CLAUDE_DIR"
else
    echo -e "${YELLOW}  Cannot create .claude in current directory (permission denied)${NC}"
    echo "  Falling back to home directory..."
    WORKSPACE_CLAUDE_DIR="$HOME/.claude"
    # Already created above
fi

# Determine the API URL that will work from the browser (needed for logging and template)
# Priority order:
# 1. OPENHEXA_PUBLIC_URL if explicitly set (manual override)
# 2. Extract from CONTENT_SECURITY_POLICY if it contains a real URL
# 3. Convert internal Docker URLs (app:8000) to localhost equivalent
# 4. Use HEXA_SERVER_URL as-is if it looks like a public URL
# 5. Ask user for input if all else fails

if [ -n "$OPENHEXA_PUBLIC_URL" ]; then
    # Manual override - use as-is
    BROWSER_API_URL="$OPENHEXA_PUBLIC_URL"
    echo "  Using OPENHEXA_PUBLIC_URL: $BROWSER_API_URL"
elif [ -n "$CONTENT_SECURITY_POLICY" ]; then
    # Try to extract a usable URL from CSP (e.g., "frame-ancestors 'self' localhost:* http://localhost:8001")
    # Look for https:// URLs first (production), then http://localhost URLs
    CSP_HTTPS_URL=$(echo "$CONTENT_SECURITY_POLICY" | grep -oE 'https://[a-zA-Z0-9.-]+' | head -1)
    CSP_LOCALHOST_URL=$(echo "$CONTENT_SECURITY_POLICY" | grep -oE 'http://localhost:[0-9]+' | head -1)

    if [ -n "$CSP_HTTPS_URL" ]; then
        BROWSER_API_URL="$CSP_HTTPS_URL"
        echo "  Detected public URL from CSP: $BROWSER_API_URL"
    elif [ -n "$CSP_LOCALHOST_URL" ]; then
        BROWSER_API_URL="$CSP_LOCALHOST_URL"
        echo "  Detected localhost URL from CSP: $BROWSER_API_URL"
    fi
fi

# Fallback logic if no URL found yet
if [ -z "$BROWSER_API_URL" ]; then
    if [[ "$HEXA_SERVER_URL" == *"app:8000"* ]]; then
        # Local development - use localhost with the exposed port
        BROWSER_API_URL="http://localhost:8001"
        echo "  Using localhost (detected local dev): $BROWSER_API_URL"
    elif [[ "$HEXA_SERVER_URL" == *"localhost"* ]] || [[ "$HEXA_SERVER_URL" == *"127.0.0.1"* ]]; then
        # Already using localhost
        BROWSER_API_URL="$HEXA_SERVER_URL"
    elif [[ "$HEXA_SERVER_URL" == https://* ]]; then
        # Production URL - use as-is
        BROWSER_API_URL="$HEXA_SERVER_URL"
        echo "  Using production URL: $BROWSER_API_URL"
    fi
fi

# Final fallback: ask user for input
if [ -z "$BROWSER_API_URL" ]; then
    echo ""
    echo -e "${YELLOW}Could not auto-detect the OpenHEXA API URL for browser access.${NC}"
    echo "This URL is used by dashboards to fetch data from the API."
    echo ""
    echo "Examples:"
    echo "  - Local development: http://localhost:8001"
    echo "  - Production: https://app.openhexa.org"
    echo ""
    read -p "Enter the OpenHEXA API URL: " BROWSER_API_URL

    if [ -z "$BROWSER_API_URL" ]; then
        echo -e "${YELLOW}Warning: No API URL provided. Dashboards may not be able to fetch data.${NC}"
        BROWSER_API_URL="http://localhost:8001"
        echo "  Defaulting to: $BROWSER_API_URL"
    fi
fi

# Remove trailing slash if present
BROWSER_API_URL="${BROWSER_API_URL%/}"

echo "  API URL for dashboards: $BROWSER_API_URL"

# Check if CLAUDE.md exists in the git repo first (prioritize repo version)
# Only generate template if not found in repo
REPO_CLAUDE_MD="$MCP_INSTALL_DIR/CLAUDE.md"

# Export variables so envsubst can use them
export BROWSER_API_URL
export HEXA_WORKSPACE
export WORKSPACE_DATABASE_DB_NAME="${WORKSPACE_DATABASE_DB_NAME:-$HEXA_WORKSPACE}"
export DASHBOARDS_DIR

# Function to substitute variables in a file
substitute_variables() {
    local src_file="$1"
    local dest_file="$2"
    # Use POSTGRES_CONN_STRING for WORKSPACE_DATABASE_URL (it has the corrected host)
    local WORKING_DB_URL="${POSTGRES_CONN_STRING:-$WORKSPACE_DATABASE_URL}"
    sed -e "s|\${BROWSER_API_URL}|$BROWSER_API_URL|g" \
        -e "s|\${HEXA_WORKSPACE}|$HEXA_WORKSPACE|g" \
        -e "s|\${WORKSPACE_DATABASE_DB_NAME}|$WORKSPACE_DATABASE_DB_NAME|g" \
        -e "s|\${DASHBOARDS_DIR}|$DASHBOARDS_DIR|g" \
        -e "s|\${WORKSPACE_DATABASE_URL}|$WORKING_DB_URL|g" \
        -e "s|\${CLAUDE_CONFIG_DIR}|$CLAUDE_CONFIG_DIR|g" \
        "$src_file" > "$dest_file"
}

# Copy and substitute CLAUDE.md from the repository
CLAUDE_MD_SOURCE="$MCP_INSTALL_DIR/CLAUDE.md"

echo "  Processing CLAUDE.md..."

if [ -f "$CLAUDE_MD_SOURCE" ]; then
    # Substitute variables and copy to workspace .claude directory
    if substitute_variables "$CLAUDE_MD_SOURCE" "$WORKSPACE_CLAUDE_DIR/CLAUDE.md"; then
        # Also copy to global Claude config directory so Claude can find it
        substitute_variables "$CLAUDE_MD_SOURCE" "$CLAUDE_CONFIG_DIR/CLAUDE.md"
        echo -e "    ${GREEN}✓ CLAUDE.md${NC}"
    else
        echo -e "    ${RED}✗ Failed to process CLAUDE.md${NC}"
        exit 1
    fi
else
    echo -e "${RED}Error: CLAUDE.md not found in repository at $MCP_INSTALL_DIR${NC}"
    echo "Please ensure the MCP repository contains CLAUDE.md"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ CLAUDE.md processed successfully${NC}"

# Show substituted values
echo ""
echo "  Substituted values:"
echo "    - BROWSER_API_URL=$BROWSER_API_URL"
echo "    - HEXA_WORKSPACE=$HEXA_WORKSPACE"
echo "    - WORKSPACE_DATABASE_DB_NAME=$WORKSPACE_DATABASE_DB_NAME"
echo "    - DASHBOARDS_DIR=$DASHBOARDS_DIR"
echo "    - WORKSPACE_DATABASE_URL=$(mask_secret "${POSTGRES_CONN_STRING:-$WORKSPACE_DATABASE_URL}")"
echo "    - CLAUDE_CONFIG_DIR=$CLAUDE_CONFIG_DIR"

echo ""

# =============================================================================
# Step 7b: Copy skills folder if it exists (with variable substitution)
# =============================================================================
SKILLS_SOURCE_DIR="$MCP_INSTALL_DIR/.claude/skills"
SKILLS_COPIED=0

if [ -d "$SKILLS_SOURCE_DIR" ]; then
    echo "  Copying skills folder with variable substitution..."

    # Iterate through each skill subdirectory
    for skill_dir in "$SKILLS_SOURCE_DIR"/*/; do
        [ -d "$skill_dir" ] || continue

        skill_name=$(basename "$skill_dir")
        echo "  Processing skill: $skill_name"

        # Create skill directories in both locations
        mkdir -p "$WORKSPACE_CLAUDE_DIR/skills/$skill_name"
        mkdir -p "$CLAUDE_CONFIG_DIR/skills/$skill_name"

        # Copy entire skill directory structure
        cp -r "$skill_dir"* "$WORKSPACE_CLAUDE_DIR/skills/$skill_name/" 2>/dev/null
        cp -r "$skill_dir"* "$CLAUDE_CONFIG_DIR/skills/$skill_name/" 2>/dev/null

        # Find and substitute variables in all .md files within the skill directory
        find "$WORKSPACE_CLAUDE_DIR/skills/$skill_name" -name "*.md" -type f | while read -r md_file; do
            # Apply variable substitution in place
            sed -i \
                -e "s|\${BROWSER_API_URL}|$BROWSER_API_URL|g" \
                -e "s|\${HEXA_WORKSPACE}|$HEXA_WORKSPACE|g" \
                -e "s|\${WORKSPACE_DATABASE_DB_NAME}|$WORKSPACE_DATABASE_DB_NAME|g" \
                -e "s|\${DASHBOARDS_DIR}|$DASHBOARDS_DIR|g" \
                -e "s|\${WORKSPACE_DATABASE_URL}|${POSTGRES_CONN_STRING:-$WORKSPACE_DATABASE_URL}|g" \
                -e "s|\${CLAUDE_CONFIG_DIR}|$CLAUDE_CONFIG_DIR|g" \
                "$md_file"
            echo -e "      ${GREEN}✓ $(basename "$md_file")${NC}"
        done

        # Also substitute in global config directory
        find "$CLAUDE_CONFIG_DIR/skills/$skill_name" -name "*.md" -type f | while read -r md_file; do
            sed -i \
                -e "s|\${BROWSER_API_URL}|$BROWSER_API_URL|g" \
                -e "s|\${HEXA_WORKSPACE}|$HEXA_WORKSPACE|g" \
                -e "s|\${WORKSPACE_DATABASE_DB_NAME}|$WORKSPACE_DATABASE_DB_NAME|g" \
                -e "s|\${DASHBOARDS_DIR}|$DASHBOARDS_DIR|g" \
                -e "s|\${WORKSPACE_DATABASE_URL}|${POSTGRES_CONN_STRING:-$WORKSPACE_DATABASE_URL}|g" \
                -e "s|\${CLAUDE_CONFIG_DIR}|$CLAUDE_CONFIG_DIR|g" \
                "$md_file"
        done

        SKILLS_COPIED=$((SKILLS_COPIED + 1))
    done

    if [ $SKILLS_COPIED -gt 0 ]; then
        echo -e "${GREEN}✓ Processed $SKILLS_COPIED skills to .claude/skills/${NC}"
    else
        echo -e "${YELLOW}⚠ No skill subdirectories found in $SKILLS_SOURCE_DIR${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Skills folder not found at $SKILLS_SOURCE_DIR (skipping)${NC}"
fi

echo ""

# =============================================================================
# Step 8: Configure MCP servers using claude mcp add
# =============================================================================
echo -e "${YELLOW}[8/8] Configuring MCP servers...${NC}"

# Use 'claude mcp add' to register MCP servers properly
# This is the recommended way to add MCP servers to Claude

# First, remove existing servers if they exist (to update them)
echo "  Removing existing MCP server configurations (if any)..."
claude mcp remove openhexa 2>/dev/null || true
claude mcp remove postgres 2>/dev/null || true

# Add OpenHEXA MCP server
echo "  Adding OpenHEXA MCP server..."
if claude mcp add openhexa \
    --scope user \
    -e HEXA_SERVER_URL="$HEXA_SERVER_URL" \
    -e HEXA_TOKEN="$HEXA_TOKEN" \
    -- python "$MCP_INSTALL_DIR/openhexa_mcp_server.py"; then
    echo -e "${GREEN}✓ Added OpenHEXA MCP server${NC}"
else
    echo -e "${RED}Error: Failed to add OpenHEXA MCP server${NC}"
fi

# Add PostgreSQL MCP server if database credentials are available
if [ "$HAS_DB" = true ] && [ -n "$POSTGRES_CONN_STRING" ]; then
    echo "  Adding PostgreSQL MCP server..."
    if claude mcp add postgres \
        --scope user \
        -e POSTGRES_CONNECTION_STRING="$POSTGRES_CONN_STRING" \
        -- python "$MCP_INSTALL_DIR/postgres_mcp_server.py"; then
        echo -e "${GREEN}✓ Added PostgreSQL MCP server${NC}"
    else
        echo -e "${RED}Error: Failed to add PostgreSQL MCP server${NC}"
    fi
fi

# List configured MCP servers
echo ""
echo "  Configured MCP servers:"
claude mcp list 2>/dev/null || echo "  (Unable to list MCP servers)"

echo -e "${GREEN}✓ MCP servers configured${NC}"

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo "MCP servers installed from: $MCP_REPO_URL"
echo "  Location: $MCP_INSTALL_DIR"
echo ""
echo "Configuration files created:"
echo "  - $MCP_INSTALL_DIR/.env"
echo "  - $HOME/.claude.json (MCP server config)"
echo "  - $WORKSPACE_CLAUDE_DIR/*.md ($MD_FILES_COPIED guideline files)"
echo "  - $CLAUDE_CONFIG_DIR/*.md (global copy of guidelines)"
echo ""
echo "MCP servers registered (user scope):"
echo "  - openhexa: OpenHEXA workspace API (datasets, pipelines, etc.)"
if [ "$HAS_DB" = true ]; then
    echo "  - postgres: PostgreSQL database queries"
fi
echo ""
echo "Workspace info:"
echo "  - OH_WORKSPACE=$HEXA_WORKSPACE"
echo "  - HEXA_DB=${WORKSPACE_DATABASE_DB_NAME:-not set}"
echo "  - DASHBOARDS_DIR=$DASHBOARDS_DIR"
echo "  - API_URL=$BROWSER_API_URL (for dashboard data fetching)"
echo ""
echo "Dashboard API endpoint:"
echo "  $BROWSER_API_URL/api/workspace/$HEXA_WORKSPACE/database/${WORKSPACE_DATABASE_DB_NAME:-$HEXA_WORKSPACE}/table/{table_name}/"
echo ""
echo -e "${GREEN}Dashboards will be saved to: $DASHBOARDS_DIR${NC}"
echo -e "${GREEN}You can run 'claude' from any directory - MCP servers are registered globally.${NC}"
echo ""
echo "To start using Claude with MCP servers:"
echo "  1. Run: claude"
echo "  2. The CLAUDE.md instructions are loaded automatically"
echo "  3. Ask Claude to explore your workspace or query your database"
echo ""

# Check if database URL was modified and warn about Jupyter kernels
if [ -n "$POSTGRES_CONN_STRING" ] && [ "$POSTGRES_CONN_STRING" != "$ORIGINAL_WORKSPACE_DATABASE_URL" ]; then
    echo -e "${YELLOW}============================================${NC}"
    echo -e "${YELLOW}  IMPORTANT: Jupyter Kernel Notice${NC}"
    echo -e "${YELLOW}============================================${NC}"
    echo ""
    echo "The database URL was updated to use a working host."
    echo "For Jupyter notebooks to use the new URL, you must:"
    echo ""
    echo "  Option 1: Restart your Jupyter kernel"
    echo "            (Kernel menu → Restart Kernel)"
    echo ""
    echo "  Option 2: Run this in your notebook:"
    echo "            import os"
    echo "            db_url = os.environ['WORKSPACE_DATABASE_URL'].replace('@test.db:', '@db:')"
    echo ""
fi
echo "Useful commands:"
echo "  claude mcp list          - List all registered MCP servers"
echo "  claude mcp remove <name> - Remove an MCP server"
echo "  claude mcp get <name>    - Test an MCP server"
echo ""
echo -e "${YELLOW}If MCP servers are not working in a session:${NC}"
echo "  Inside Claude, type: /mcp"
echo "  This will show MCP status and allow you to enable servers"
echo ""
echo "Example prompts:"
echo '  - "List all datasets in my workspace"'
echo '  - "Show me the tables in my database"'
echo '  - "Create a dashboard showing data from the users table"'
echo ""
echo -e "${YELLOW}Note: Make sure you have a valid Anthropic API key set:${NC}"
echo "  export ANTHROPIC_API_KEY=your-api-key"
echo ""
echo -e "${BLUE}Troubleshooting:${NC}"
echo "  - Run 'claude mcp get openhexa' to test the OpenHEXA server"
echo "  - Run 'claude --version' to check your Claude Code version"
echo "  - Ensure you're running the latest: npm update -g @anthropic-ai/claude-code"
echo ""
