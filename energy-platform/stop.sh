#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/infrastructure/docker/docker-compose.yml"
ENV_FILE="$SCRIPT_DIR/.env"
PODMAN_STORAGE_CONF="/tmp/energy-platform-storage.conf"
CONTAINER_RUNTIME="docker"

docker_is_podman_wrapper() {
  local docker_path
  docker_path="$(command -v docker 2>/dev/null || true)"
  [[ -n "$docker_path" ]] && grep -q 'exec /usr/bin/podman' "$docker_path"
}

if command -v podman >/dev/null 2>&1 && docker_is_podman_wrapper; then
  CONTAINER_RUNTIME="podman"
  export DOCKER_HOST="unix:///run/user/$(id -u)/podman/podman.sock"
  if [[ -f "$PODMAN_STORAGE_CONF" ]]; then
    export CONTAINERS_STORAGE_CONF="$PODMAN_STORAGE_CONF"
  fi
fi

if [[ "$CONTAINER_RUNTIME" == "podman" ]]; then
  if command -v podman-compose >/dev/null 2>&1; then
    COMPOSE_CMD=(podman-compose)
  else
    echo "podman-compose is required when Podman is used as the runtime." >&2
    exit 1
  fi
elif docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "Docker Compose is required but was not found." >&2
  exit 1
fi

"${COMPOSE_CMD[@]}" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" down
