.PHONY: build run run-multi clean help

IMAGE_NAME := claude-sandbox
CONTAINER_NAME := claude-sandbox-instance

help:
	@echo "Claude Sandbox Container - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make build        - Build the container image"
	@echo "  make run          - Run single Claude session (direct mount, recommended)"
	@echo "  make run-multi    - Run multiple Claude sessions (default: 2)"
	@echo "  make run-copy     - Run with copy-on-start (isolated credentials)"
	@echo "  make run-no-mount - Run without mounting credentials"
	@echo "  make copy-creds   - Copy credentials to running container"
	@echo "  make run-firewall - Run with firewall enabled (requires root podman)"
	@echo "  make clean        - Remove container image"
	@echo "  make help         - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make build"
	@echo "  make run                    # Direct mount (credentials stay in sync)"
	@echo "  make run-multi N=3          # Three sessions with mounted credentials"
	@echo "  make run-copy               # Copy-on-start (more isolated)"
	@echo "  make run-firewall"
	@echo ""
	@echo "Credential Options:"
	@echo "  1. Direct mount (run):     Credentials always in sync, simplest (recommended)"
	@echo "  2. Copy-on-start (run-copy): Credentials isolated, changes don't persist"
	@echo "  3. Manual copy (run-no-mount + copy-creds): For advanced use cases"
	@echo ""
	@echo "Documentation:"
	@echo "  See ~/.dotfiles/docs/claude-sandbox.md for complete documentation"
	@echo ""
	@echo "Notes:"
	@echo "  - Firewall is disabled by default for rootless podman compatibility"
	@echo "  - Use run-firewall for network isolation (requires root podman + --privileged)"

build:
	@echo "Building with BuildKit cache support..."
	BUILDKIT_PROGRESS=plain podman build \
		--layers=true \
		-t $(IMAGE_NAME) \
		-f Containerfile .

run:
	@mkdir -p ~/.config/claude ~/.cache/uv
	@./sync-credentials.sh || echo "⚠ Could not sync credentials - will need to auth in container"
	@if [ -f .claude-oauth-creds.json ]; then \
		podman run -it --rm \
			--name $(CONTAINER_NAME) \
			-v $(PWD):/workspace/$(shell basename $(PWD)) \
			-v ~/.config/claude:/home/agent/.config/claude \
			-v $(PWD)/.claude-oauth-creds.json:/tmp/host-claude-oauth.json:ro \
			-v ~/.cache/uv:/home/agent/.cache/uv \
			--network="host" \
			-w /workspace/$(shell basename $(PWD)) \
			$(IMAGE_NAME); \
	else \
		podman run -it --rm \
			--name $(CONTAINER_NAME) \
			-v $(PWD):/workspace/$(shell basename $(PWD)) \
			-v ~/.config/claude:/home/agent/.config/claude \
			-v ~/.cache/uv:/home/agent/.cache/uv \
			--network="host" \
			-w /workspace/$(shell basename $(PWD)) \
			$(IMAGE_NAME); \
	fi

run-multi:
	@mkdir -p ~/.config/claude ~/.cache/uv
	$(eval N := $(or $(N),2))
	podman run -it --rm \
		--name $(CONTAINER_NAME) \
		-v $(PWD):/workspace/$(shell basename $(PWD)) \
		-v ~/.config/claude:/home/agent/.config/claude \
		-v ~/.cache/uv:/home/agent/.cache/uv \
		--network="host" \
		-w /workspace/$(shell basename $(PWD)) \
		$(IMAGE_NAME) -n$(N)

run-firewall:
	@mkdir -p ~/.config/claude ~/.cache/uv
	podman run -it --rm \
		--name $(CONTAINER_NAME) \
		-v $(PWD):/workspace/$(shell basename $(PWD)) \
		-v ~/.config/claude:/home/agent/.config/claude \
		-v ~/.cache/uv:/home/agent/.cache/uv \
		--network="host" \
		--privileged \
		-e ENABLE_FIREWALL=1 \
		-w /workspace/$(shell basename $(PWD)) \
		$(IMAGE_NAME)

run-copy:
	@mkdir -p ~/.config/claude ~/.cache/uv
	@echo "Running with copy-on-start (credentials isolated from host)..."
	podman run -it --rm \
		--name $(CONTAINER_NAME) \
		-v $(PWD):/workspace/$(shell basename $(PWD)) \
		-v ~/.config/claude:/tmp/host-claude-creds/config:ro \
		-v ~/.claude.json:/tmp/host-claude-creds/claude.json:ro \
		-v ~/.cache/uv:/home/agent/.cache/uv \
		--network="host" \
		-w /workspace/$(shell basename $(PWD)) \
		$(IMAGE_NAME)

run-no-mount:
	@echo "Starting container without mounting credentials..."
	@echo "Use './copy-credentials.sh' in another terminal to copy credentials"
	podman run -it --rm \
		--name $(CONTAINER_NAME) \
		-v $(PWD):/workspace/$(shell basename $(PWD)) \
		--network="host" \
		-w /workspace/$(shell basename $(PWD)) \
		$(IMAGE_NAME)

copy-creds:
	./copy-credentials.sh $(CONTAINER_NAME)

clean:
	podman rmi $(IMAGE_NAME)
