https://hermes-agent.nousresearch.com/docs/getting-started/quickstart

# dnf install libatomic    >> pre-req
# curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
→ Updating /root/.hermes/hermes-agent (main)
✓ config prepared in /root/.hermes
✓ added ~/.local/bin to PATH in /root/.profile

# hermes pm install --without cua-driver    >> This driver allows agent interaction with native desktop.
# systemctl --user stop hermes-gateway.service
# systemctl --user disable hermes-gateway.service
# systemctl --user status hermes-gateway.service
# ps -aux | grep hermes

# hermes setup model, hermes setup


