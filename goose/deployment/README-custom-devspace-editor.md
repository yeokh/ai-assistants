Create a Custom Dedicated ConfigMap to Add the Web Terminal Editor
==================================================================

OpenShift Dev Spaces requires a separate ConfigMap for custom editor
definitions. The operator scans `openshift-devspaces` for ConfigMaps with
specific labels and merges them into the dashboard.

This folder includes `che-web-terminal-latest.yaml` (Web Terminal / ttyd IDE).

Step 1: Create the ConfigMap
----------------------------

```bash
oc create configmap custom-editor-web-terminal \
  --from-file=che-web-terminal-latest.yaml \
  -n openshift-devspaces
```

Step 2: Apply required labels
-----------------------------

```bash
oc label configmap custom-editor-web-terminal \
  app.kubernetes.io/part-of=che.eclipse.org \
  app.kubernetes.io/component=editor-definition \
  -n openshift-devspaces --overwrite
```

Step 3: Verify
--------------

```bash
oc get configmap custom-editor-web-terminal -n openshift-devspaces
```

Refresh the Dev Spaces dashboard. **Web Terminal** should appear alongside
VS Code / JetBrains.

Using it with this workspace
----------------------------

The `devfile.yaml` pins:

```yaml
attributes:
  che-editor: che-incubator/che-web-terminal/latest
```

Or open via factory URL:

```
https://<devspaces-host>/dashboard/#/load-factory?url=<repo-url>&che-editor=che-incubator/che-web-terminal/latest
```

References
----------

- https://eclipse.dev/che/docs/stable/administration-guide/configuring-editors-definitions/
- https://github.com/eclipse-che/che-operator/blob/main/editors-definitions/che-web-terminal-latest.yaml
