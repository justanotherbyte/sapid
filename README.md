# Sapid

A high-level framework for building GitHub applications in Python.


## Core Features
- Async
- Proper ratelimit handling
- Handles interactions for you (responding with appropriate response status codes etc.)
- Minimal raw payloads. Most are being parsed internally into pythonic objects.
- Runs its own webhook server, with a no-bloat async web server (aiohttp)

## Example
### Basic bot example

```py
from sapid import GitBot

bot = GitBot(
    pem_file_fp="bot.pem",
    app_id="...", # Found on github.
    webhook_secret="...", # Set on github.
    client_secret="..." # Generate on github.
)

@bot.event
async def on_sapid_tcp_ready(host, port):
    print(f"tcp running on http://{host}:{port}")
    print(bot.user.name)
    print(bot.user.description)

bot.run(host="127.0.0.1", port=3000)
```

### Locking Issue on Star
I know this isn't something you'd usually do, but hey, it showcases something.
```py
from sapid import GitBot, Repository, IssueLockReason

bot = GitBot(
    pem_file_fp="bot.pem",
    app_id="...", # Found on github.
    webhook_secret="...", # Set on github.
    client_secret="..." # Generate on github.
)

@bot.event
async def on_repository_star_update(action: str, repo: Repository):
    issue = await repo.fetch_issue(1)
    await issue.create_comment("Hello! Locking Issue")
    await issue.lock(reason=IssueLockReason.TOO_HEATED)
```