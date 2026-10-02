# Goose — OpenShift Dev Spaces

Workspace image with Goose pre-installed. Uses the **Web Terminal** editor
(not VS Code) so you land in a terminal and run `goose` directly.

## Architecture

```
Dev Spaces
├── Web Terminal editor (ttyd)   ← che-web-terminal (registered once on cluster)
└── goose workspace container    ← Containerfile-devspaces
      ├── goose CLI (/usr/local/bin)
      ├── /projects              ← workspace PVC (cloned repo)
      └── /home/user/.config/goose ← goose-config PVC
```

## Files

| File | Purpose |
|------|---------|
| `Containerfile-devspaces` | UDI ubi9 + community Goose |
| `devfile.yaml` | Workspace definition (pins Web Terminal) |
| `secret-api-keys-devspaces.yaml` | Optional auto-mounted API keys Secret |
| `che-web-terminal-latest.yaml` | Editor definition |
| `README-custom-devspace-editor.md` | How to register the editor |

---

## 1. Build and push

From `goose/`:

```bash
podman build \
  -t quay.io/kenghua_yeo/goose-devspaces:latest \
  -f deployment/Containerfile-devspaces \
  deployment/
podman push quay.io/kenghua_yeo/goose-devspaces:latest
```

### Install method

Community download script with `GOOSE_BIN_DIR=/usr/local/bin` (see `../README.md`).

### Alternative: Red Hat / EPEL

```dockerfile
RUN dnf install -y \
      https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm \
    && dnf install -y goose \
    && dnf clean all
```

---

## 2. Register Web Terminal editor (once per cluster)

See [README-custom-devspace-editor.md](README-custom-devspace-editor.md).

---

## 3. API keys

**Option A — User Preferences:** Dev Spaces → User Menu → Environment Variables  
(`GOOSE_PROVIDER`, `GOOSE_MODEL`, `OPENAI_API_KEY`, …)

**Option B — Secret** in your Dev Spaces namespace:

```bash
oc project <username>-devspaces
# Edit placeholders first, then:
oc apply -f secret-api-keys-devspaces.yaml
```

---

## 4. Start workspace

If the Git root is `goose/` (this folder is `deployment/`), point Dev Spaces at the nested devfile:

```
https://<devspaces-host>/dashboard/#/load-factory?url=<goose-repo-url>&devfilePath=deployment/devfile.yaml&che-editor=che-incubator/che-web-terminal/latest
```

If the Git root is `ai-assistants/`, use `devfilePath=goose/deployment/devfile.yaml` instead.

In the terminal:

```bash
goose configure   # first time
goose session
```

Or use the Dev Spaces command palette entries defined in `devfile.yaml`.
