#!/usr/bin/env bash
# Minimal Goose launcher: prompts for an OpenAI-compatible custom provider,
# writes custom_providers/custom_<name>.json + config.yaml + secrets.yaml
# (same layout as `goose configure`), then starts goose.
set -euo pipefail

command -v goose >/dev/null || { echo "goose not found in PATH" >&2; exit 1; }

# Ask goose where it reads its config; fall back to the XDG default.
CFG_DIR="$(goose info 2>/dev/null | sed -n 's/^Config dir: *\([^ ]*\).*/\1/p')"
CFG_DIR="${CFG_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/goose}"
CONFIG="$CFG_DIR/config.yaml"
SECRETS="$CFG_DIR/secrets.yaml"
PROVIDER_DIR="$CFG_DIR/custom_providers"

DEF_PROVIDER="maas"
DEF_URL="https://maas-rhdp.apps.maas.redhatworkshops.io"
DEF_MODEL="qwen38-27b"
CONTEXT_LIMIT=32768

# List configured providers, their models and whether an API key exists.
show_providers() {
  local active names n f models cfg_model env key
  active="$(sed -n 's/^active_provider: *"\{0,1\}\([^"]*\)"\{0,1\} *$/\1/p' "$CONFIG" 2>/dev/null || true)"
  names="$( { awk '/^providers:/{p=1;next} p&&/^[^ ]/{p=0} p&&/^  [^ ]/{sub(/^  /,"");sub(/:.*/,"");print}' "$CONFIG" 2>/dev/null
              for f in "$PROVIDER_DIR"/*.json; do if [[ -e "$f" ]]; then basename "$f" .json; fi; done; } | sort -u)"
  echo "Configured providers ($CFG_DIR):"
  [[ -z "$names" ]] && { echo "  (none)"; echo; return; }
  for n in $names; do
    f="$PROVIDER_DIR/$n.json"
    cfg_model="$(awk -v n="$n" '/^providers:/{p=1;next} p&&/^[^ ]/{p=0} p&&/^  [^ ]/{c=($0=="  " n ":")} p&&c&&/^    model:/{print $2}' "$CONFIG" 2>/dev/null)"
    if [[ -f "$f" ]]; then
      models="$(grep -o '"name": *"[^"]*"' "$f" | sed -n '2,$s/.*: *"\(.*\)"/\1/p' | paste -sd, -)"
      env="$(sed -n 's/.*"api_key_env": *"\([^"]*\)".*/\1/p' "$f")"
    else
      models=""; env="$(tr 'a-z-' 'A-Z_' <<<"$n")_API_KEY"
    fi
    if [[ -z "$env" ]]; then key="n/a"
    elif grep -q "^$env:" "$SECRETS" 2>/dev/null || [[ -n "$(printenv "$env" 2>/dev/null)" ]]; then key="yes ($env)"
    else key="NO ($env)"; fi
    printf '  %s%s\n    config model: %s\n    listed models: %s\n    api key: %s\n' \
      "$n" "$([[ "$n" == "$active" ]] && echo ' [active]')" "${cfg_model:--}" "${models:--}" "$key"
  done
  echo
}

ask() { # ask VAR "prompt" default
  local reply
  read -r -p "$2 [$3]: " reply
  printf -v "$1" '%s' "${reply:-$3}"
}

show_providers
ask NAME "Provider name" "$DEF_PROVIDER"
ask BASE_URL "Base URL" "$DEF_URL"
ask MODEL "Model" "$DEF_MODEL"
read -r -p "API key (blank = keep existing): " API_KEY

# Goose stores custom providers as custom_<name> (file, config key, provider id)
# and the key env var as CUSTOM_<NAME>_API_KEY (hyphens kept).
[[ "$NAME" =~ ^[a-z0-9-]+$ ]] || { echo "Provider name must match [a-z0-9-]+" >&2; exit 1; }
PROVIDER="custom_$NAME"
KEY_ENV="CUSTOM_$(tr 'a-z' 'A-Z' <<<"$NAME")_API_KEY"

# OpenAI-compatible endpoint: append /v1/chat/completions unless present.
ENDPOINT="${BASE_URL%/}"
case "$ENDPOINT" in
  */chat/completions) ;;
  */v1) ENDPOINT="$ENDPOINT/chat/completions" ;;
  *) ENDPOINT="$ENDPOINT/v1/chat/completions" ;;
esac

mkdir -p "$PROVIDER_DIR"
touch "$CONFIG" "$SECRETS"
chmod 600 "$SECRETS"

# Replace-or-append a top-level "KEY: value" line in a YAML file.
yaml_set() { # yaml_set file key value
  local tmp esc=${3//\\/\\\\}
  esc=${esc//\"/\\\"}
  tmp="$(mktemp)"
  grep -v "^$2:" "$1" >"$tmp" || true
  printf '%s: "%s"\n' "$2" "$esc" >>"$tmp"
  cat "$tmp" >"$1"; rm -f "$tmp"
}

# Own file per provider, so a real "openai" provider/key is never touched.
# Minimal, version-tolerant format: full endpoint URL and a numeric
# context_limit (goose 1.45 rejects null; newer versions accept a number).
cat >"$PROVIDER_DIR/$PROVIDER.json" <<EOF
{
  "name": "$PROVIDER",
  "engine": "openai",
  "display_name": "$NAME",
  "description": "Custom $NAME provider",
  "api_key_env": "$KEY_ENV",
  "base_url": "$ENDPOINT",
  "models": [{ "name": "$MODEL", "context_limit": $CONTEXT_LIMIT }],
  "supports_streaming": true,
  "requires_auth": true
}
EOF

# config.yaml: active_provider + providers.<provider> {enabled, model, configured}
yaml_set "$CONFIG" active_provider "$PROVIDER"
grep -q '^providers:' "$CONFIG" || echo 'providers:' >>"$CONFIG"
tmp="$(mktemp)"
awk -v p="$PROVIDER" -v m="$MODEL" '
  /^providers:/ {
    print
    printf "  %s:\n    enabled: true\n    model: %s\n    configured: true\n", p, m
    inprov = 1; skip = 0; next
  }
  inprov && /^[^ ]/ { inprov = 0; skip = 0 }
  inprov && /^  [^ ]/ { skip = ($0 == "  " p ":") }
  inprov && skip { next }
  { print }
' "$CONFIG" >"$tmp"
cat "$tmp" >"$CONFIG"; rm -f "$tmp"

[[ -n "$API_KEY" ]] && yaml_set "$SECRETS" "$KEY_ENV" "$API_KEY"
if ! grep -q "^$KEY_ENV:" "$SECRETS"; then
  echo "Warning: no $KEY_ENV in $SECRETS." >&2
fi

# Read secrets from secrets.yaml rather than the system keyring.
export GOOSE_DISABLE_KEYRING=1

echo "Starting goose: provider=$PROVIDER model=$MODEL url=$ENDPOINT"
exec goose
