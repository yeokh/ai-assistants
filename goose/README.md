Community Goose
===============
https://github.com/aaif-goose/goose

Goose CLI:
$ sudo dnf install bzip2  # Pre-req to install
$ curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
$ curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | CONFIGURE=false bash

$ goose configure
$ cat /root/.config/goose/config.yaml

$ goose
$ goose session list
$ goose session -n 20260628_3 --resume
$ goose update

https://goose-docs.ai/docs/tutorials/goose-in-docker

.goosehints - project/folder level instructions file.




RED HAT Version of Goose
========================
Goose with RHEL - https://interact.redhat.com/share/Z42Lt4N7qGKWKSNhmHhk

https://access.redhat.com/articles/7142302

Use instructions to run agent jobs with Goose:
goose run -i <path to instruction> -s

ACP / A2A tooling
=================
ACP chat, HTTP+SSE bridge, web UI, and related client/server artifacts have
moved to the A2A project:

- Local: `/root/a2a`
- GitHub: https://github.com/yeokh/a2a

That repo covers using Goose via `goose serve` (ACP) or `a2a-proxy --backend goose`
(A2A façade over `goose acp`). See its README for setup and usage.

ACP protocol reference:
https://block-goose.mintlify.app/advanced/acp-protocol
