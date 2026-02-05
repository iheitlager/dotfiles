# Claude Team Container Build

IMAGE := claudeteam:latest

.PHONY: build build-no-cache test clean

build: ## Build container image
	podman build -t $(IMAGE) .

build-no-cache: ## Build without cache
	podman build --no-cache -t $(IMAGE) .

test: build ## Test the container starts
	podman run --rm -it $(IMAGE) shell -c "echo 'Container OK' && claude --version && gh --version && uv --version"

clean: ## Remove image
	podman rmi $(IMAGE) 2>/dev/null || true

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
