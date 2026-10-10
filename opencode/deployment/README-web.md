# OpenCode Web UI — Container & OpenShift Deployment

Run OpenCode as a browser web application with
[`opencode web`](https://opencode.ai/docs/web/). No ttyd.

The container listens on **0.0.0.0:4096**, starts with cwd
**/home/opencode/workspace**, and expects **`OPENCODE_SERVER_PASSWORD`** for
HTTP Basic Auth (username defaults to `opencode`).

## Files

| File | Purpose |
|------|---------|
| `Containerfile-web` | Image build |
| `entrypoint.sh` | Workspace cwd + `opencode web` startup |
| `opencode.json` | Default config (model + server bind) |
| `openshift/web-pvc.yaml` | Config (1 Gi) + workspace (5 Gi) PVCs |
| `openshift/web-secret.yaml` | Server password + API keys Secret template |
| `openshift/web-deployment.yaml` | Deployment |
| `openshift/web-service.yaml` | ClusterIP Service :4096 |
| `openshift/web-route.yaml` | HTTPS Route (edge TLS) |
| `opencode-web-catalog-template.yaml` | Software Catalog Template |

## Supported providers

Set the matching API key env/Secret. Default model uses `provider/model` form
via `OPENCODE_MODEL`.

| Provider | Example `OPENCODE_MODEL` | API key env |
|----------|--------------------------|-------------|
| OpenAI | `openai/gpt-4o` | `OPENAI_API_KEY` |
| Anthropic | `anthropic/claude-sonnet-4-5` | `ANTHROPIC_API_KEY` |
| Google Gemini | `google/...` | `GOOGLE_API_KEY` |
| OpenRouter | `openrouter/...` | `OPENROUTER_API_KEY` |

## Persistence

| PVC | Mount | Contents |
|-----|-------|----------|
| `*-config` | `~/.config/opencode` (`subPath: config`) | Config (`opencode.json`) |
| `*-config` | `~/.local/share/opencode` (`subPath: share`) | Auth, sessions, DB |
| `*-workspace` | `/home/opencode/workspace` | Default project root |

## CORS

**Not required** for normal OpenShift Route access: the built-in web UI is
served from the same host as the API (same-origin).

Set `OPENCODE_CORS` (Template parameter / env) only if a **separate** frontend
origin must call this server. Use full origins, e.g.
`https://my-frontend.apps.example.com`.

---

## 1. Build and push

From `opencode/`:

```bash
export IMAGE=quay.io/kenghua_yeo/opencode-web:v1

podman build -t "${IMAGE}" -f deployment/Containerfile-web deployment/
podman login quay.io
podman push "${IMAGE}"
```

### Install method (community)

The Containerfile installs OpenCode with:

```bash
curl -fsSL https://opencode.ai/install | bash -s -- --no-modify-path
```

The binary is installed to `/usr/local/bin/opencode`.

---

## 2. Test locally with Podman

```bash
podman volume create opencode-web-config
podman volume create opencode-web-share
podman volume create opencode-web-workspace

podman run --rm -p 4096:4096 \
  -e OPENCODE_SERVER_PASSWORD=changeme \
  -e OPENCODE_SERVER_USERNAME=opencode \
  -e OPENCODE_MODEL=openai/gpt-4o \
  -e OPENAI_API_KEY=sk-... \
  -v opencode-web-config:/home/opencode/.config/opencode \
  -v opencode-web-share:/home/opencode/.local/share/opencode \
  -v opencode-web-workspace:/home/opencode/workspace \
  quay.io/kenghua_yeo/opencode-web:v1
```

Open **http://localhost:4096** and sign in with user `opencode` / your password.

Anthropic / OpenRouter examples — same pattern with the matching env vars.

Debug shell:

```bash
podman run -it --rm -p 4096:4096 \
  -e OPENCODE_SERVER_PASSWORD=changeme \
  -e OPENAI_API_KEY=sk-... \
  -v opencode-web-config:/home/opencode/.config/opencode \
  -v opencode-web-share:/home/opencode/.local/share/opencode \
  -v opencode-web-workspace:/home/opencode/workspace \
  quay.io/kenghua_yeo/opencode-web:v1 \
  bash
```

---

## 3. Deploy on OpenShift (manifests)

```bash
oc new-project opencode   # or: oc project <existing>

# Prefer oc create secret (see openshift/web-secret.yaml header)
oc create secret generic opencode-web-secrets \
  --from-literal=OPENCODE_SERVER_PASSWORD='changeme' \
  --from-literal=OPENCODE_SERVER_USERNAME=opencode \
  --from-literal=OPENCODE_MODEL=openai/gpt-4o \
  --from-literal=OPENAI_API_KEY=sk-...

oc apply -f openshift/web-pvc.yaml
oc apply -f openshift/web-deployment.yaml
oc apply -f openshift/web-service.yaml
oc apply -f openshift/web-route.yaml

oc get route opencode-web
```

---

## 4. Deploy via catalog Template

```bash
oc process -f opencode-web-catalog-template.yaml \
  -p APP_NAME=opencode-web \
  -p IMAGE_NAME=quay.io/kenghua_yeo/opencode-web:v1 \
  -p OPENCODE_SERVER_PASSWORD='changeme' \
  -p OPENCODE_SERVER_USERNAME=opencode \
  -p OPENCODE_MODEL=openai/gpt-4o \
  -p OPENAI_API_KEY=sk-... \
  | oc apply -f -
```

Register cluster-wide (optional):

```bash
oc apply -f opencode-web-catalog-template.yaml -n openshift
```

### Template parameters (summary)

| Parameter | Required | Default | Purpose |
|-----------|----------|---------|---------|
| `APP_NAME` | yes | `opencode-web` | Resource name prefix |
| `IMAGE_NAME` | yes | `quay.io/kenghua_yeo/opencode-web:v1` | Image pullspec |
| `PORT` | yes | `4096` | Container / Service port |
| `OPENCODE_HOSTNAME` | yes | `0.0.0.0` | Listen address for Service/Route |
| `STARTUP_COMMAND` | yes | entrypoint | JSON array command |
| `OPENCODE_SERVER_PASSWORD` | **yes** | _(none)_ | Web UI Basic Auth password |
| `OPENCODE_SERVER_USERNAME` | yes | `opencode` | Web UI Basic Auth username |
| `OPENCODE_MODEL` | yes | `openai/gpt-4o` | Default `provider/model` |
| `OPENCODE_CORS` | no | `""` | Extra CORS origins (optional) |
| `CONFIG_STORAGE_SIZE` | yes | `1Gi` | Config + share PVC |
| `WORKSPACE_STORAGE_SIZE` | yes | `5Gi` | Workspace PVC |
| `OPENAI_API_KEY` | no | | Provider key |
| `ANTHROPIC_API_KEY` | no | | Provider key |
| `OPENROUTER_API_KEY` | no | | Provider key |
| `GOOGLE_API_KEY` | no | | Provider key |

Each parameter also has a longer `description` in the Template YAML (shown in
the OpenShift Software Catalog UI).
