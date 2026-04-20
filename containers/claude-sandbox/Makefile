.PHONY: build clean help

IMAGE   := claude-sandbox:local
RUNTIME := $(shell colima status >/dev/null 2>&1 && echo docker || (podman info >/dev/null 2>&1 && echo podman) || echo none)

help:
	@echo "Claude Sandbox - Containerfile build"
	@echo ""
	@echo "  make build   Build the container image"
	@echo "  make clean   Remove image and persistent volumes"
	@echo ""
	@echo "Usage (via claude-sandbox wrapper):"
	@echo "  claude-sandbox [DIR...]               Run in current (or given) directories"
	@echo "  claude-sandbox --yolo [DIR...]         Skip permission prompts"
	@echo "  claude-sandbox --ephemeral [DIR...]    No persistent volumes"
	@echo "  claude-sandbox --ro [DIR...]           Read-only workspace"
	@echo "  claude-sandbox --gh [DIR...]           Forward GH credentials"
	@echo "  claude-sandbox --aws [DIR...]          Forward AWS config/SSO"
	@echo "  claude-sandbox --glab [DIR...]         Forward GitLab credentials"
	@echo "  claude-sandbox ~/a ~/b -- --resume     Multiple workspaces + claude flags"

build:
	@[ "$(RUNTIME)" = "none" ] && echo "No container runtime available. Install colima or podman." && exit 1 || true
	$(RUNTIME) build -t $(IMAGE) -f Containerfile .

clean:
	$(RUNTIME) rmi $(IMAGE) 2>/dev/null || true
	$(RUNTIME) volume rm claude-sandbox-root claude-sandbox-home 2>/dev/null || true
