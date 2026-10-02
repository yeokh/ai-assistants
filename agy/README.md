https://antigravity.google/docs/cli/overview/
# curl -fsSL https://antigravity.google/cli/install.sh | bash
✅ Antigravity CLI installed successfully at /root/.local/bin/agy

# agy -c -p "chat request, continue from previous session..."


Configurations/Settings:
# ls /root/.gemini/antigravity-cli
# cat /root/.gemini/antigravity-cli/settings.json

Set the tone and communication style of Antigravity in three ways:
### 1. Project-Specific Tone (Recommended)
  Create a GEMINI.md or AGENTS.md file at the root of your
  workspace (or inside .agents/rules/). Antigravity
  automatically discovers and loads these rule files on
  every interaction.

### 2. Global Tone (All Workspaces/Projects)
  Create a GEMINI.md or AGENTS.md file at:
  ~/.gemini/config/

  Antigravity discovers and loads these every interaction.
  It also checks project/workspace level rules.

### 3. In-Session Prompting & /learn to persist in workspace
  • Instruct directly in prompt/chat. 
  • Persisting with /learn command to save to workspace.
