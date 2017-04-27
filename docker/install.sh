#!/usr/bin/env bash

# tab completion for docker
curl -L https://raw.githubusercontent.com/docker/compose/$(docker-compose version --short)/contrib/completion/bash/docker-compose -o $(brew --prefix)/etc/bash_completion.d/docker-compose

