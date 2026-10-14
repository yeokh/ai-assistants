#!/usr/bin/env bash
# Minimal Pi launcher: prompts for an OpenAI-compatible custom provider,
# updates models.json + auth.json + settings.json in the Pi agent dir
# (only this provider's entries), then starts pi.
set -euo pipefail

command -v pi >/dev/null || { echo "pi not found in PATH" >&2; exit 1; }
command -v node >/dev/null || { echo "node not found in PATH (needed to edit JSON)" >&2; exit 1; }

export AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"

DEF_PROVIDER="maas"
DEF_URL="https://maas-rhdp.apps.maas.redhatworkshops.io"
DEF_MODEL="qwen38-27b"
export CONTEXT_LIMIT=32768

# List configured providers, their models and whether an API key exists.
show_providers() {
  node - <<'JS'
const fs = require("fs"), path = require("path");
const dir = process.env.AGENT_DIR;
const read = (f) => {
  try { return JSON.parse(fs.readFileSync(path.join(dir, f), "utf8")); }
  catch (e) { if (e.code === "ENOENT") return {}; throw new Error(`${f}: ${e.message}`); }
};
const models = read("models.json").providers || {};
const auth = read("auth.json");
const settings = read("settings.json");
const names = [...new Set([...Object.keys(models), ...Object.keys(auth)])].sort();
console.log(`Configured providers (${dir}):`);
if (!names.length) console.log("  (none)");
for (const n of names) {
  const def = n === settings.defaultProvider;
  const ids = ((models[n] || {}).models || []).map((m) => m.id).join(",");
  const key = auth[n] ? "auth.json" : (models[n] || {}).apiKey ? "models.json" : null;
  console.log(`  ${n}${def ? " [default]" : ""}`);
  console.log(`    default model: ${def ? settings.defaultModel || "-" : "-"}`);
  console.log(`    listed models: ${ids || "-"}`);
  console.log(`    api key: ${key ? `yes (${key})` : "NO"}`);
}
console.log();
JS
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

[[ "$NAME" =~ ^[a-z0-9-]+$ ]] || { echo "Provider name must match [a-z0-9-]+" >&2; exit 1; }

# Pi appends /chat/completions itself: baseUrl must be the API root (.../v1).
API_ROOT="${BASE_URL%/}"
API_ROOT="${API_ROOT%/chat/completions}"
[[ "$API_ROOT" == */v1 ]] || API_ROOT="$API_ROOT/v1"

mkdir -p "$AGENT_DIR"
export NAME MODEL API_ROOT API_KEY

# Replace only this provider's entries; keep everything else in each file.
node - <<'JS'
const fs = require("fs"), path = require("path");
const dir = process.env.AGENT_DIR;
const { NAME, MODEL, API_ROOT, API_KEY, CONTEXT_LIMIT } = process.env;
const read = (f) => {
  try { return JSON.parse(fs.readFileSync(path.join(dir, f), "utf8")); }
  catch (e) { if (e.code === "ENOENT") return {}; throw new Error(`${f}: ${e.message}`); }
};
const write = (f, obj, mode) => {
  const p = path.join(dir, f);
  fs.writeFileSync(p, JSON.stringify(obj, null, 2) + "\n", { mode });
  fs.chmodSync(p, mode);
};

const models = read("models.json");
models.providers = models.providers || {};
models.providers[NAME] = {
  baseUrl: API_ROOT,
  api: "openai-completions",
  models: [{ id: MODEL, reasoning: false, contextWindow: Number(CONTEXT_LIMIT) }],
};
write("models.json", models, 0o644);

const auth = read("auth.json");
if (API_KEY) auth[NAME] = { type: "api_key", key: API_KEY };
if (!auth[NAME]) console.error(`Warning: no API key for ${NAME} in auth.json.`);
write("auth.json", auth, 0o600);

const settings = read("settings.json");
settings.defaultProvider = NAME;
settings.defaultModel = MODEL;
write("settings.json", settings, 0o644);
JS

echo "Starting pi: provider=$NAME model=$MODEL url=$API_ROOT"
exec pi
