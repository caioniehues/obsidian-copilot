# Build base image
FROM python:3.9.16-slim as base

RUN apt-get update && apt-get install -y make curl

WORKDIR /obsidian-copilot

ENV PYTHONUNBUFFERED TRUE

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && pip list

# Built slim image
FROM python:3.9.16-slim as app

WORKDIR /obsidian-copilot

COPY --from=base /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
# copy the repo contents into the container
COPY . .

RUN chmod +x /obsidian-copilot/build.sh

# Claude Code CLI setup
# Option 1: Mount from host (recommended)
# When running container, mount Claude CLI: -v /usr/local/bin/claude:/usr/local/bin/claude:ro
# Option 2: Copy from host during build (requires multi-stage build)
# COPY --from=host /usr/local/bin/claude /usr/local/bin/claude

# Set environment variables for Claude
ENV CLAUDE_CODE_PATH=/usr/local/bin/claude
ENV USE_CLAUDE_BACKEND=false
ENV MAX_CONTEXT_TOKENS=100000

# Note: ANTHROPIC_API_KEY should be set at runtime if using Claude API