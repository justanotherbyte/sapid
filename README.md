# GitBot

A high-level framework for building GitHub applications in Python.


## Core Features
- Async
- Proper ratelimit handling
- Handles interactions for you (responding with appropriate response status codes etc.)
- Minimal raw payloads. Most are being parsed internally into pythonic objects.
- Runs its own webhook server, with a no-bloat async web server (aiohttp)