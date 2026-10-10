#!/usr/bin/env bash
set -euo pipefail

# OpenShift runs containers as an arbitrary UID; ensure writable dirs exist.
export HOME="${HOME:-/home/opencode}"
mkdir -p \
  "${HOME}/.config/opencode" \
  "${HOME}/.local/share/opencode" \
  "${HOME}/workspace" 2>/dev/null || true

# Default project / workspace for the web UI (cwd becomes the project root).
cd "${HOME}/workspace"

# Optional model override via OPENCODE_MODEL (provider/model), unless the
# caller already set OPENCODE_CONFIG_CONTENT.
if [[ -n "${OPENCODE_MODEL:-}" && -z "${OPENCODE_CONFIG_CONTENT:-}" ]]; then
  # Minimal JSON; OpenCode merges this as a runtime config override.
  export OPENCODE_CONFIG_CONTENT="{\"model\":\"${OPENCODE_MODEL}\"}"
fi

# If args were provided (e.g. debug shell), run them instead of the web UI.
if [[ $# -gt 0 ]]; then
  case "$1" in
    bash|/bin/bash|sh|/bin/sh)
      shift
      exec /bin/bash "$@"
      ;;
    opencode)
      shift
      exec opencode "$@"
      ;;
    *)
      exec "$@"
      ;;
  esac
fi

hostname="${OPENCODE_HOSTNAME:-0.0.0.0}"
port="${OPENCODE_PORT:-4096}"

args=(web --hostname "${hostname}" --port "${port}")

# Optional extra CORS origins (comma- or space-separated full origins).
# Not required when the browser loads the built-in web UI from the same
# OpenShift Route host (same-origin). Set when a separate frontend origin
# must call this server.
if [[ -n "${OPENCODE_CORS:-}" ]]; then
  # shellcheck disable=SC2086
  for origin in ${OPENCODE_CORS//,/ }; do
    [[ -n "${origin}" ]] || continue
    args+=(--cors "${origin}")
  done
fi

if [[ -z "${OPENCODE_SERVER_PASSWORD:-}" ]]; then
  echo "warning: OPENCODE_SERVER_PASSWORD is unset; opencode web will be unsecured" >&2
fi

exec opencode "${args[@]}"
