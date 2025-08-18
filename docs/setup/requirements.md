# 📋 System Requirements

> Prerequisites and system requirements for Obsidian Copilot

## Minimum Requirements

### Hardware
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 5GB free space
- **CPU**: Modern multi-core processor (2015 or newer)
- **Network**: Stable internet for Claude API calls

### Operating System
- **macOS**: 10.15 (Catalina) or higher
- **Linux**: Ubuntu 20.04+ or equivalent
- **Windows**: Windows 10/11 with WSL2

## Required Software

### 1. Obsidian
- **Version**: 0.12.0 or higher
- **Download**: https://obsidian.md
- **Configuration**: Community plugins must be enabled

### 2. Container Runtime (Choose One)

#### Option A: Docker Desktop
- **Version**: 20.10 or higher
- **Download**: https://www.docker.com/products/docker-desktop
- **Verify**: `docker --version`

#### Option B: Podman
- **Version**: 3.0 or higher
- **Download**: https://podman.io/getting-started/installation
- **Verify**: `podman --version`

### 3. Node.js
- **Version**: 18.0 or higher
- **Download**: https://nodejs.org
- **Verify**: `node --version`
- **NPM**: Included with Node.js

### 4. Python
- **Version**: 3.11 or higher
- **Download**: https://python.org
- **Verify**: `python3 --version`
- **pip**: Should be included

### 5. Git
- **Version**: Any recent version
- **Download**: https://git-scm.com
- **Verify**: `git --version`

### 6. Claude Access (Choose One)

#### Option A: Claude Code CLI (Recommended)
- **Installation**: https://claude.ai/code
- **Verify**: `claude --version`
- **Benefits**: Local processing, no API key needed

#### Option B: Claude API Key
- **Obtain from**: Anthropic Console
- **Format**: `sk-ant-api03-...`
- **Note**: Requires paid account

### 7. Basic Memory MCP Server
- **Purpose**: Agent memory and learning
- **Repository**: https://github.com/waldzx/basic-memory
- **Installation**: Follow Basic Memory setup guide
- **Verify**: Check MCP server is running

## Recommended Software

### Performance Tools
- **Redis**: For caching (optional but recommended)
  ```bash
  brew install redis  # macOS
  apt install redis   # Ubuntu
  ```

### Development Tools
- **VS Code**: For editing configuration
- **Postman**: For testing API endpoints
- **Docker Desktop**: For container management

## Version Compatibility Matrix

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| Obsidian | 0.12.0 | Latest | Community plugins required |
| Docker | 20.10 | Latest | Or Podman 3.0+ |
| Node.js | 18.0 | 20.0+ | LTS version preferred |
| Python | 3.11 | 3.11+ | 3.12 also supported |
| Claude CLI | Latest | Latest | Keep updated |
| RAM | 8GB | 16GB+ | More for large vaults |

## Platform-Specific Requirements

### macOS
- Xcode Command Line Tools:
  ```bash
  xcode-select --install
  ```
- Homebrew (recommended):
  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```

### Linux (Ubuntu/Debian)
- Build essentials:
  ```bash
  sudo apt update
  sudo apt install build-essential curl wget
  ```
- Docker dependencies:
  ```bash
  sudo apt install apt-transport-https ca-certificates gnupg lsb-release
  ```

### Windows
- **WSL2 Required**: Windows Subsystem for Linux v2
  ```powershell
  wsl --install
  ```
- **Docker Desktop for Windows**: With WSL2 backend
- **Git Bash**: For Unix-like commands

## Network Requirements

### Ports
The following ports must be available:
- **8000**: FastAPI backend
- **9200**: OpenSearch
- **6379**: Redis (if using)
- **3000**: Development server (optional)

### Firewall
Allow outbound connections to:
- `api.anthropic.com` (for Claude API)
- `huggingface.co` (for model downloads)
- Docker Hub (for container images)

## Vault Requirements

### Size Considerations
- **Small Vault** (<100 notes): All features work smoothly
- **Medium Vault** (100-1000 notes): Default settings optimal
- **Large Vault** (1000+ notes): May need performance tuning
- **Very Large** (5000+ notes): Requires optimization settings

### Structure Requirements
- Standard Obsidian vault structure
- Markdown files (`.md` extension)
- UTF-8 encoding
- No special characters in folder names

## Pre-Installation Checklist

Before proceeding with installation, verify:

- [ ] Operating system meets requirements
- [ ] Docker or Podman installed and running
- [ ] Node.js v18+ installed
- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] Obsidian installed with community plugins enabled
- [ ] Claude access configured (CLI or API key)
- [ ] At least 5GB free disk space
- [ ] Required ports are available
- [ ] Internet connection for initial setup

## Performance Recommendations

### For Optimal Performance
- **SSD Storage**: Significantly improves indexing speed
- **16GB+ RAM**: Allows larger context windows
- **Multi-core CPU**: Enables parallel processing
- **Gigabit Network**: Faster model downloads

### For Large Vaults (1000+ notes)
- **32GB RAM**: Recommended for smooth operation
- **NVMe SSD**: For fastest indexing
- **8+ CPU cores**: For parallel agent execution
- **Dedicated GPU**: Optional, for future features

## Troubleshooting Requirements

### Common Requirement Issues

**"Command not found"**
- Ensure software is in PATH
- Restart terminal after installation
- Use full path to executable

**"Permission denied"**
- Check file permissions
- Run with appropriate privileges
- Ensure user owns Obsidian vault

**"Port already in use"**
- Check for conflicting services
- Change port in configuration
- Stop conflicting service

**"Out of memory"**
- Increase Docker memory limit
- Reduce context window size
- Close unnecessary applications

---

**Navigation**: [← Documentation](../README.md) | [Installation →](./installation.md)