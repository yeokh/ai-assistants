# Goose — Deployment Artifacts

Container images, OpenShift manifests, catalog Template, and Dev Spaces
devfile for [Goose](https://github.com/aaif-goose/goose).

| Path | Purpose |
|------|---------|
| `Containerfile-ttyd` | Web terminal image (ttyd + goose) |
| `Containerfile-devspaces` | Dev Spaces workspace image |
| `config.yaml` | Default goose config baked into images |
| `entrypoint.sh` | Optional entrypoint helper |
| `goose-ttyd-catalog-template.yaml` | OpenShift Software Catalog Template |
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
| `quay.io/kenghua_yeo/goose-ttyd` | `v1` |
| `quay.io/kenghua_yeo/goose-devspaces` | `latest` |

## Quick start

**ttyd (local):** see [README-ttyd.md](README-ttyd.md)

**Dev Spaces:** see [README-devspaces.md](README-devspaces.md) and
[README-custom-devspace-editor.md](README-custom-devspace-editor.md)

**Catalog:**

```bash
oc process -f goose-ttyd-catalog-template.yaml \
  -p OPENAI_API_KEY=sk-... \
  -p GOOSE_PROVIDER=openai \
  -p GOOSE_MODEL=gpt-4o \
  | oc apply -f -
```

## Goose install method

Images use the **community download script** (same as `../README.md`):

```bash
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh \
  | CONFIGURE=false GOOSE_BIN_DIR=/usr/local/bin bash
```

For **Red Hat / EPEL** packaged goose, see the Alternative section in
`README-ttyd.md` / `README-devspaces.md` (or the comments in the Containerfiles).
