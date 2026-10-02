# Pi — Deployment Artifacts

Container images, OpenShift manifests, catalog Template, and Dev Spaces
devfile for the [pi coding agent](https://github.com/earendil-works/pi).

| Path | Purpose |
|------|---------|
| `Containerfile-ttyd` | Web terminal image (ttyd + pi) |
| `Containerfile-devspaces` | Dev Spaces workspace image |
| `pi-ttyd-catalog-template.yaml` | OpenShift Software Catalog Template |
| `devfile.yaml` | Dev Spaces workspace (Web Terminal editor) |
| `che-web-terminal-latest.yaml` | Editor definition for Dev Spaces |
| `secret-api-keys-devspaces.yaml` | API keys Secret for Dev Spaces |
| `openshift/` | Direct `oc apply` manifests for ttyd |
| `README-ttyd.md` | Build / Podman / OpenShift for ttyd |
| `README-devspaces.md` | Dev Spaces setup |
| `README-custom-devspace-editor.md` | Register Web Terminal editor |

## Images

| Image | Tag |
|-------|-----|
| `quay.io/kenghua_yeo/pi-ttyd` | `v1` |
| `quay.io/kenghua_yeo/pi-devspaces` | `v1` |

## Quick start

**ttyd (local):** see [README-ttyd.md](README-ttyd.md)

**Dev Spaces:** see [README-devspaces.md](README-devspaces.md) and
[README-custom-devspace-editor.md](README-custom-devspace-editor.md)

**Catalog:**

```bash
oc process -f pi-ttyd-catalog-template.yaml \
  -p ANTHROPIC_API_KEY=sk-ant-... \
  | oc apply -f -
```

## Bases

| Image | Base |
|-------|------|
| ttyd | `registry.redhat.io/ubi9/nodejs-24-minimal` |
| Dev Spaces | `quay.io/redhat-cop/devspaces-base:latest` |
