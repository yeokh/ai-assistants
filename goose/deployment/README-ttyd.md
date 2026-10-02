# Goose ttyd Web Terminal — Container & OpenShift Deployment

Run Goose as an interactive web terminal using [ttyd](https://github.com/tsl0922/ttyd).
The container starts **bash** on port **7681** so you can run `goose configure`
then `goose session`.

## Files

| File | Purpose |
|------|---------|
| `Containerfile-ttyd` | Image build |
| `openshift/ttyd-pvc.yaml` | Config (1 Gi) + workspace (5 Gi) PVCs |
| `openshift/ttyd-secret.yaml` | API keys Secret template |
| `openshift/ttyd-deployment.yaml` | Deployment |
| `openshift/ttyd-service.yaml` | ClusterIP Service :7681 |
| `openshift/ttyd-route.yaml` | HTTPS Route (edge TLS) |
| `goose-ttyd-catalog-template.yaml` | Software Catalog Template |

## Supported providers

| Provider | `GOOSE_PROVIDER` | API key env |
|----------|------------------|-------------|
| OpenAI | `openai` | `OPENAI_API_KEY` |
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` |
| Google Gemini | `google` | `GOOGLE_API_KEY` |
| OpenRouter | `openrouter` | `OPENROUTER_API_KEY` |
| Ollama | `ollama` | _(none)_ — set `OLLAMA_HOST` |

---

## 1. Build and push

From `goose/`:

```bash
export IMAGE=quay.io/kenghua_yeo/goose-ttyd:v1

podman build -t "${IMAGE}" -f deployment/Containerfile-ttyd deployment/
podman login quay.io
podman push "${IMAGE}"
```

### Install method (community)

The Containerfile installs Goose with:

```bash
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh \
  | CONFIGURE=false GOOSE_BIN_DIR=/usr/local/bin bash
```

Requires `bzip2` (installed in the image).

### Alternative: Red Hat / EPEL package

To use packaged `goose` from EPEL instead of the download script, replace the
curl install in `Containerfile-ttyd` with:

```dockerfile
RUN dnf install -y \
      https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm \
    && dnf install -y goose \
    && rpm -q goose-redhat >/dev/null 2>&1 \
         && { echo "error: goose-redhat must not be present for generic providers" >&2; exit 1; } \
         || true \
    && dnf clean all
```

Red Hat Goose docs: https://access.redhat.com/articles/7142302

---

## 2. Test locally with Podman

```bash
podman volume create goose-ttyd-config
podman volume create goose-ttyd-workspace

podman run --rm -p 7681:7681 \
  -e GOOSE_PROVIDER=openai \
  -e GOOSE_MODEL=gpt-4o \
  -e OPENAI_API_KEY=sk-... \
  -v goose-ttyd-config:/home/goose/.config/goose \
  -v goose-ttyd-workspace:/home/goose/workspace \
  quay.io/kenghua_yeo/goose-ttyd:v1
```

Open **http://localhost:7681**, then:

```bash
goose configure   # if needed
goose session
```

Anthropic / OpenRouter examples — same pattern with the matching env vars.

Debug shell:

```bash
podman run -it --rm -p 7681:7681 \
  -e GOOSE_PROVIDER=openai \
  -e GOOSE_MODEL=gpt-4o \
  -e OPENAI_API_KEY=sk-... \
  -v goose-ttyd-config:/home/goose/.config/goose \
  -v goose-ttyd-workspace:/home/goose/workspace \
  --entrypoint /bin/bash \
  quay.io/kenghua_yeo/goose-ttyd:v1
```

---

## 3. Deploy on OpenShift (manifests)

```bash
oc new-project goose   # or: oc project <existing>

# Prefer oc create secret (see openshift/ttyd-secret.yaml header)
oc create secret generic goose-ttyd-api-keys \
  --from-literal=GOOSE_PROVIDER=openai \
  --from-literal=GOOSE_MODEL=gpt-4o \
  --from-literal=OPENAI_API_KEY=sk-...

oc apply -f openshift/ttyd-pvc.yaml
oc apply -f openshift/ttyd-deployment.yaml
oc apply -f openshift/ttyd-service.yaml
oc apply -f openshift/ttyd-route.yaml

oc get route goose-ttyd
```

---

## 4. Deploy via catalog Template

```bash
oc process -f goose-ttyd-catalog-template.yaml \
  -p APP_NAME=goose-ttyd \
  -p IMAGE_NAME=quay.io/kenghua_yeo/goose-ttyd:v1 \
  -p GOOSE_PROVIDER=openai \
  -p GOOSE_MODEL=gpt-4o \
  -p OPENAI_API_KEY=sk-... \
  | oc apply -f -
```

Register cluster-wide (optional):

```bash
oc apply -f goose-ttyd-catalog-template.yaml -n openshift
```
