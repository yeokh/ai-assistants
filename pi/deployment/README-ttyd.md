# pi-ttyd — Container & OpenShift Deployment

Web terminal for the [pi](https://github.com/earendil-works/pi) coding agent via
[ttyd](https://github.com/tsl0922/ttyd). Starts in **bash** on port **7681**.

## Architecture

```
Browser → OpenShift Route (TLS) → Service :7681 → Pod (ttyd → bash / pi)
                                                         │
                                              PVC: pi-agent-home
                                              /opt/app-root/.pi/agent
```

## Files

| File | Purpose |
|------|---------|
| `Containerfile-ttyd` | Image build |
| `openshift/ttyd-secret.yaml` | LLM API keys |
| `openshift/ttyd-pvc.yaml` | 2 Gi PVC for pi state |
| `openshift/ttyd-deployment.yaml` | Deployment |
| `openshift/ttyd-service.yaml` | ClusterIP :7681 |
| `openshift/ttyd-route.yaml` | Edge HTTPS Route |
| `pi-ttyd-catalog-template.yaml` | Software Catalog Template |

---

## 1. Build and push

From `pi/deployment/` (or adjust `-f` / context):

```bash
export IMAGE=quay.io/kenghua_yeo/pi-ttyd:v1

podman build -t "${IMAGE}" -f Containerfile-ttyd .
podman login quay.io
podman push "${IMAGE}"
```

From `pi/`:

```bash
podman build -t "${IMAGE}" -f deployment/Containerfile-ttyd deployment/
podman push "${IMAGE}"
```

---

## 2. Test locally with Podman

```bash
podman volume create pi-ttyd-agent

podman run --rm -p 7681:7681 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e OPENAI_API_KEY=sk-... \
  -v pi-ttyd-agent:/opt/app-root/.pi/agent \
  quay.io/kenghua_yeo/pi-ttyd:v1
```

Open **http://localhost:7681**, then:

```bash
pi          # or /login inside pi if needed
```

---

## 3. Deploy on OpenShift (manifests)

```bash
oc new-project pi   # or: oc project <existing>

oc create secret generic pi-ttyd-api-keys \
  --from-literal=ANTHROPIC_API_KEY=sk-ant-... \
  --from-literal=OPENAI_API_KEY=sk-...

# Or edit and apply openshift/ttyd-secret.yaml (no real keys in git)

oc apply -f openshift/ttyd-pvc.yaml
oc apply -f openshift/ttyd-deployment.yaml
oc apply -f openshift/ttyd-service.yaml
oc apply -f openshift/ttyd-route.yaml

oc get route pi-ttyd
```

---

## 4. Deploy via catalog Template

```bash
oc process -f pi-ttyd-catalog-template.yaml \
  -p APP_NAME=pi-ttyd \
  -p IMAGE_NAME=quay.io/kenghua_yeo/pi-ttyd:v1 \
  -p ANTHROPIC_API_KEY=sk-ant-... \
  | oc apply -f -
```

Register cluster-wide (optional):

```bash
oc apply -f pi-ttyd-catalog-template.yaml -n openshift
```
