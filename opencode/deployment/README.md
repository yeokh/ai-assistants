# OpenCode — Deployment Artifacts

Container image, OpenShift manifests, and catalog Template for
[OpenCode](https://github.com/anomalyco/opencode) as a **web application**
(`opencode web`). No ttyd and no Dev Spaces / devfile.

| Path | Purpose |
|------|---------|
| `Containerfile-web` | Web UI image (`opencode web`) |
| `opencode.json` | Default OpenCode config baked into the image |
| `entrypoint.sh` | Starts web UI in `/home/opencode/workspace` |
| `opencode-web-catalog-template.yaml` | OpenShift Software Catalog Template |
| `openshift/` | Direct `oc apply` manifests |
| `README-web.md` | Build / Podman / OpenShift for the web UI |

## Images

| Image | Tag |
|-------|-----|
| `quay.io/kenghua_yeo/opencode-web` | `v1` |

## Quick start

**Web UI (local):** see [README-web.md](README-web.md)

**Catalog:**

```bash
oc process -f opencode-web-catalog-template.yaml \
  -p OPENCODE_SERVER_PASSWORD='changeme' \
  -p OPENAI_API_KEY=sk-... \
  -p OPENCODE_MODEL=openai/gpt-4o \
  | oc apply -f -
```

After deploy, open the Route URL and sign in with username `opencode` (or
`OPENCODE_SERVER_USERNAME`) and the server password you set.

## OpenCode install method

Images use the **official install script** (same as `../README.md`):

```bash
curl -fsSL https://opencode.ai/install | bash -s -- --no-modify-path
```

The binary is copied to `/usr/local/bin/opencode` so it is on `PATH` for any UID.
