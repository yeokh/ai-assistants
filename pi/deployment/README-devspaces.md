# Pi — OpenShift Dev Spaces

Workspace image with the pi CLI pre-installed. Uses the **Web Terminal**
editor (not VS Code) so you land in a terminal and run `pi` directly.

## Architecture

```
Dev Spaces
├── Web Terminal editor (ttyd)   ← che-web-terminal (registered once on cluster)
└── pi workspace container       ← Containerfile-devspaces
      ├── pi CLI (npm global)
      ├── Node.js 24, ripgrep, fd, git, …
      ├── /projects              ← workspace PVC (cloned repo)
      └── /home/user/.pi/agent   ← pi-agent-home PVC
```

## Files

| File | Purpose |
|------|---------|
| `Containerfile-devspaces` | `devspaces-base` + Node 24 + pi |
| `devfile.yaml` | Workspace definition (pins Web Terminal) |
| `secret-api-keys-devspaces.yaml` | Optional auto-mounted API keys Secret |
| `che-web-terminal-latest.yaml` | Editor definition |
| `README-custom-devspace-editor.md` | How to register the editor |

---

## 1. Build and push

From `pi/deployment/`:

```bash
podman build \
  -t quay.io/kenghua_yeo/pi-devspaces:v1 \
  -f Containerfile-devspaces .
podman push quay.io/kenghua_yeo/pi-devspaces:v1
```

---

## 2. Register Web Terminal editor (once per cluster)

See [README-custom-devspace-editor.md](README-custom-devspace-editor.md).

---

## 3. API keys

**Option A — User Preferences:** Dev Spaces → User Menu → Environment Variables  
(`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, …)

**Option B — Secret** in your Dev Spaces namespace:

```bash
oc project <username>-devspaces
# Edit placeholders first, then:
oc apply -f secret-api-keys-devspaces.yaml
```

---

## 4. Start workspace

If the Git root is `pi/` (this folder is `deployment/`), point Dev Spaces at the nested devfile:

```
https://<devspaces-host>/dashboard/#/load-factory?url=<pi-repo-url>&devfilePath=deployment/devfile.yaml&che-editor=che-incubator/che-web-terminal/latest
```

If the Git root is `ai-assistants/`, use `devfilePath=pi/deployment/devfile.yaml` instead.

In the terminal:

```bash
pi
# /login   # if interactive auth is required
```
