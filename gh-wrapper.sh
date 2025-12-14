#!/bin/bash
# Wrapper to run gh CLI from a container on bootc/image-mode systems
# Persists auth in ~/.config/gh

mkdir -p "${HOME}/.config/gh"

GITCONFIG_MOUNT=""
if [ -f "${HOME}/.gitconfig" ]; then
  GITCONFIG_MOUNT="-v ${HOME}/.gitconfig:/root/.gitconfig:ro,Z"
fi

podman run --rm -it \
  --security-opt label=disable \
  -v "${PWD}:/workspace:Z" \
  -v "${HOME}/.config/gh:/root/.config/gh:Z" \
  -v "${HOME}/.ssh:/root/.ssh:ro,Z" \
  $GITCONFIG_MOUNT \
  -w /workspace \
  localhost/gh-cli "$@"
