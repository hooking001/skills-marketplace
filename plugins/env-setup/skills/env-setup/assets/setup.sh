#!/usr/bin/env bash
set -euo pipefail

# Environment setup script for AI coding agents
# Installs herdr, rtk, effortless (conditional), and configures Serena MCP

export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:${PATH}"

echo "=== [1/4] Installing herdr ==="
if command -v herdr >/dev/null 2>&1; then
    echo "✓ herdr is already installed: $(herdr --version 2>/dev/null || echo 'installed')"
else
    echo "Installing herdr via https://herdr.dev/install.sh..."
    if curl -fsSL https://herdr.dev/install.sh | sh; then
        echo "✓ herdr installed successfully."
    elif command -v cargo >/dev/null 2>&1; then
        echo "Install script failed; trying cargo install herdr..."
        cargo install herdr
        echo "✓ herdr installed via cargo."
    elif command -v brew >/dev/null 2>&1; then
        echo "Install script failed; trying brew install herdr..."
        brew install herdr
        echo "✓ herdr installed via brew."
    else
        echo "⚠ Failed to install herdr. Please check network or install manually."
    fi
fi

if command -v herdr >/dev/null 2>&1; then
    echo "Installing herdr integrations for codex and claude..."
    herdr integration install codex || true
    herdr integration install claude || true
fi

echo ""
echo "=== [2/4] Installing rtk (Rust Token Killer) ==="
if command -v rtk >/dev/null 2>&1; then
    echo "✓ rtk is already installed: $(rtk --version 2>/dev/null || echo 'installed')"
else
    echo "Installing rtk via install.sh..."
    if curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh; then
        echo "✓ rtk installed successfully."
    elif command -v brew >/dev/null 2>&1; then
        echo "Install script failed; trying brew install rtk-ai/tap/rtk..."
        brew install rtk-ai/tap/rtk
        echo "✓ rtk installed via brew."
    elif command -v cargo >/dev/null 2>&1; then
        echo "Install script failed; trying cargo install..."
        cargo install --git https://github.com/rtk-ai/rtk --branch master rtk
        echo "✓ rtk installed via cargo."
    else
        echo "⚠ Failed to install rtk. Please check network or install manually."
    fi
fi

# Configure rtk for available agents
if command -v rtk >/dev/null 2>&1; then
    if command -v claude >/dev/null 2>&1; then
        echo "Configuring rtk for Claude Code..."
        rtk init -g || true
    fi
    if command -v codex >/dev/null 2>&1; then
        echo "Configuring rtk for Codex..."
        rtk init -g --codex || true
    fi
fi

echo ""
echo "=== [3/4] Installing effortless plugin (Claude Code) ==="
if command -v claude >/dev/null 2>&1; then
    echo "✓ claude binary found at $(command -v claude)."
    echo "Adding marketplace HeyCubit/effortless..."
    claude plugin marketplace add HeyCubit/effortless || true
    echo "Installing effortless plugin..."
    claude plugin install effortless@effortless || true
    echo "✓ effortless installation attempted."
else
    echo "ℹ claude binary not found. Skipping effortless plugin installation."
fi

echo ""
echo "=== [4/4] Configuring Serena MCP ==="
# Ensure uv is installed
if ! command -v uv >/dev/null 2>&1; then
    echo "uv not found; installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:${PATH}"
fi

# Connect Serena MCP to Claude Code if available
if command -v claude >/dev/null 2>&1; then
    echo "Adding Serena MCP to Claude Code (scope: user)..."
    claude mcp add --scope user serena -- uvx --from git+https://github.com/oraios/serena serena-mcp-server --context claude-code || true
fi

# Connect Serena MCP to Codex if available
if command -v codex >/dev/null 2>&1; then
    echo "Adding Serena MCP to Codex..."
    codex mcp add serena -- uvx --from git+https://github.com/oraios/serena serena-mcp-server --context codex || true
else
    # Also ensure ~/.codex/config.toml has serena configuration if ~/.codex directory exists or is created
    CODEX_DIR="${HOME}/.codex"
    CODEX_CONFIG="${CODEX_DIR}/config.toml"
    mkdir -p "${CODEX_DIR}"
    if [ ! -f "${CODEX_CONFIG}" ] || ! grep -q "\[mcp_servers\.serena\]" "${CODEX_CONFIG}" 2>/dev/null; then
        echo "Writing Serena MCP configuration to ${CODEX_CONFIG}..."
        cat >> "${CODEX_CONFIG}" << 'EOF'

[mcp_servers.serena]
command = "uvx"
args = ["--from", "git+https://github.com/oraios/serena", "serena-mcp-server", "--context", "codex"]
EOF
        echo "✓ Added Serena MCP to ${CODEX_CONFIG}."
    else
        echo "✓ Serena MCP already configured in ${CODEX_CONFIG}."
    fi
fi

echo ""
echo "=== Setup complete! ==="
