.PHONY: help init clean test lint format build install update version changelog release dev docs

# Variables
PROJECT_NAME := repo-template
VERSION_FILE := version.json

## help: Show available commands
help:
	@echo "=== Available Commands ==="
	@echo ""
	@echo "  make help          - Show this help message"
	@echo "  make init          - Initialize project"
	@echo "  make install       - Install dependencies"
	@echo "  make dev           - Run development environment"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Lint code"
	@echo "  make format        - Format code"
	@echo "  make build         - Build project"
	@echo "  make clean         - Clean temporary files"
	@echo "  make docs          - Generate documentation"
	@echo "  make version       - Show current version"
	@echo "  make version-bump  - Bump version"
	@echo "  make changelog     - Generate CHANGELOG"
	@echo "  make release       - Create release"
	@echo "  make update        - Update template"
	@echo ""

## init: Initialize project
init:
	@echo "[INFO] Initializing project..."
	@echo "TODO: Setup git hooks, create configuration files"

## install: Install dependencies
install:
	@echo "[INFO] Installing dependencies..."
	@echo "TODO: Install Copier and other required tools"

## dev: Run development environment
dev:
	@echo "[INFO] Starting development environment..."
	@echo "TODO: Start local development server"

## test: Run tests
test:
	@echo "[INFO] Running tests..."
	@echo "TODO: Run template validation tests"

## lint: Lint code
lint:
	@echo "[INFO] Linting code..."
	@echo "TODO: Check markdown files, yaml configurations"

## format: Format code
format:
	@echo "[INFO] Formatting code..."
	@echo "TODO: Format markdown, yaml and other files"

## build: Build project
build:
	@echo "[INFO] Building project..."
	@echo "TODO: Prepare template for publication"

## clean: Clean temporary files
clean:
	@echo "[INFO] Cleaning temporary files..."
	@echo "TODO: Remove temporary files and cache"

## docs: Generate documentation
docs:
	@echo "[INFO] Generating documentation..."
	@echo "TODO: Generate HTML documentation from markdown"

## version: Show current version
version:
	@echo "[INFO] Reading version from $(VERSION_FILE)..."
	@echo "TODO: Parse and display version"

## version-bump: Bump version
version-bump:
	@echo "[INFO] Bumping version..."
	@echo "TODO: Automatically update version based on commits"

## changelog: Generate CHANGELOG
changelog:
	@echo "[INFO] Generating CHANGELOG..."
	@echo "TODO: Generate CHANGELOG.md from git commit history"

## release: Create release
release:
	@echo "[INFO] Creating release..."
	@echo "TODO: Create git tag and publish release"

## update: Update template
update:
	@echo "[INFO] Updating template..."
	@echo "TODO: Update template to latest version"

# Default target
.DEFAULT_GOAL := help

