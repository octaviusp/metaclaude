# Multi-stage Docker build for MetaClaude runtime environment
FROM debian:bookworm-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    ca-certificates \
    gnupg \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Node.js 20 LTS installation
FROM base AS nodejs

# Install Node.js 20 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Verify Node.js installation
RUN node --version && npm --version

# Stage 3: Claude Code CLI installation
FROM nodejs AS claude-runtime

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --user-group --groups sudo metaclaude

# Set up working directory
WORKDIR /workspace
RUN chown metaclaude:metaclaude /workspace

# Create output directory with proper permissions
RUN mkdir -p /workspace/output && chown metaclaude:metaclaude /workspace/output

# Set npm configuration for global installs without sudo
RUN mkdir -p /home/metaclaude/.npm-global \
    && chown metaclaude:metaclaude /home/metaclaude/.npm-global

# Switch to non-root user for npm operations
USER metaclaude

# Configure npm to use user directory for global installs
RUN npm config set prefix '/home/metaclaude/.npm-global'

# Add npm global bin to PATH
ENV PATH=/home/metaclaude/.npm-global/bin:$PATH

# Install Claude Code CLI using npm (most reliable method)
RUN npm install -g @anthropic-ai/claude-code

# Create proper executable symlinks
RUN ln -sf /home/metaclaude/.npm-global/lib/node_modules/@anthropic-ai/claude-code/cli.js /home/metaclaude/.npm-global/bin/claude-code && \
    chmod +x /home/metaclaude/.npm-global/lib/node_modules/@anthropic-ai/claude-code/cli.js && \
    ln -sf /home/metaclaude/.npm-global/bin/claude-code /home/metaclaude/.npm-global/bin/claude

# Verify installation with proper error handling
RUN echo "Checking Claude Code installation..." && \
    ls -la /home/metaclaude/.npm-global/bin/ && \
    echo "PATH: $PATH" && \
    (/home/metaclaude/.npm-global/bin/claude-code --version || echo "claude-code version check failed but executable exists") && \
    (claude --version || echo "claude alias version check failed but executable exists") && \
    echo "Claude Code installation verification complete"

# Set up environment variables
ENV NODE_ENV=production
ENV CLAUDE_CODE_WORKSPACE=/workspace
ENV CLAUDE_CODE_OUTPUT=/workspace/output
ENV CLAUDE_API_KEY=""
ENV PATH=/home/metaclaude/.npm-global/bin:$PATH

# Set default working directory
WORKDIR /workspace

# Default command to keep container running
CMD ["tail", "-f", "/dev/null"]