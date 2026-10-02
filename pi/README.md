https://github.com/earendil-works/pi/tree/main/packages/coding-agent
https://pi.dev/docs/latest/quickstart

Install nodejs prerequisites:
> Install nvm, reload shell, install/use Node.js 24 - https://github.com/nvm-sh/nvm#installing-and-updating 
$ curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
$ source ~/.bashrc
$ nvm install 24
$ nvm use 24
$ nvm ls

> Install pi
$ curl -fsSL https://pi.dev/install.sh | sh
$ npm list -g --depth=0

$ export ANTHROPIC_API_KEY=<redacted-anthropic-api-key>
$ pi
  /login

$ cat ~/.pi/agent/auth.json


