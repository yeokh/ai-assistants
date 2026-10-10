https://junie.jetbrains.com/

# dnf install unzip
# curl -fsSL https://junie.jetbrains.com/install.sh | bash
# junie

Junie reads AGENTS.md by default for guidelines. When working on a project, Junie automatically discovers and loads
guidelines in this order:
1. .junie/AGENTS.md in the project root
2. AGENTS.md in the project root, combined with .junie/playbook.md and .junie/rules/*.md


