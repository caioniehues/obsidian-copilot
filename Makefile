# Obsidian Copilot - Plugin-Only Makefile
# Simplified for TypeScript plugin development

# Check whether the `OBSIDIAN_PATH` env var is set
ifndef OBSIDIAN_PATH
$(error OBSIDIAN_PATH is not set, please set it to your Obsidian vault path)
endif

# Plugin installation and development
install-plugin:
	mkdir -p ${OBSIDIAN_PATH}.obsidian/plugins/copilot/
	cp plugin/main.js plugin/styles.css plugin/manifest.json "${OBSIDIAN_PATH}.obsidian/plugins/copilot/"

sync-plugin:
	cp -R ${OBSIDIAN_PATH}.obsidian/plugins/copilot/* plugin/

# Plugin development commands
build-plugin:
	cd plugin && npm run build

dev-plugin:
	cd plugin && npm run dev

test-plugin:
	cd plugin && npm test

test-plugin-watch:
	cd plugin && npm run test:watch

test-plugin-coverage:
	cd plugin && npm run test:coverage

# Plugin installation and setup
setup-plugin:
	@echo "🔧 Setting up Obsidian Copilot Plugin..."
	@echo "Installing dependencies..."
	cd plugin && npm install
	@echo "Building plugin..."
	cd plugin && npm run build
	@echo "Installing to Obsidian..."
	make install-plugin
	@echo "✅ Plugin setup complete!"
	@echo "Enable the plugin in Obsidian Settings > Community Plugins"

# Development workflow
dev-setup:
	@echo "🛠️  Setting up development environment..."
	cd plugin && npm install
	@echo "✅ Development setup complete!"
	@echo "Run 'make dev-plugin' to start development mode"

# Help
help:
	@echo "📖 Obsidian Copilot - Plugin Commands"
	@echo ""
	@echo "🚀 Setup Commands:"
	@echo "  make setup-plugin     Complete plugin setup and installation"
	@echo "  make dev-setup        Setup development environment"
	@echo ""
	@echo "🔧 Development Commands:"
	@echo "  make build-plugin     Build the plugin"
	@echo "  make dev-plugin       Development mode with hot reload"
	@echo "  make install-plugin   Install plugin to Obsidian"
	@echo "  make sync-plugin      Sync changes from Obsidian back to repo"
	@echo ""
	@echo "🧪 Testing Commands:"
	@echo "  make test-plugin      Run tests"
	@echo "  make test-plugin-watch      Run tests in watch mode"
	@echo "  make test-plugin-coverage   Run tests with coverage"
	@echo ""
	@echo "Required environment variable:"
	@echo "  OBSIDIAN_PATH=/path/to/obsidian-vault/ (note: trailing slash required)"

.PHONY: install-plugin sync-plugin build-plugin dev-plugin test-plugin test-plugin-watch test-plugin-coverage
.PHONY: setup-plugin dev-setup help