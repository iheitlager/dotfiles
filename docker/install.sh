#!/usr/bin/env bash

# tab completion for docker
# read: https://blog.fabric8.io/enable-bash-completion-for-kubernetes-with-kubectl-506bc89fe79e#.kh4uuccdx
curl -L https://raw.githubusercontent.com/docker/compose/$(docker-compose version --short)/contrib/completion/bash/docker-compose > /etc/bash_completion.d/docker-compose
