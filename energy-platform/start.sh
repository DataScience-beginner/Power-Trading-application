#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/infrastructure/docker/docker-compose.yml"
DEFAULT_ENV_FILE="$SCRIPT_DIR/.env.example"
ENV_FILE="$SCRIPT_DIR/.env"
PODMAN_STORAGE_CONF="/tmp/energy-platform-storage.conf"
CONTAINER_RUNTIME=""

if [[ ! -f "$ENV_FILE" ]]; then
  cp "$DEFAULT_ENV_FILE" "$ENV_FILE"
  echo "Created .env from .env.example. Review it before production use."
fi

configure_podman_storage() {
  mkdir -p /tmp/energy-platform-podman-storage /tmp/energy-platform-podman-runroot
  cat > "$PODMAN_STORAGE_CONF" <<'EOF'
[storage]
driver = "overlay"
runroot = "/tmp/energy-platform-podman-runroot"
graphroot = "/tmp/energy-platform-podman-storage"
rootless_storage_path = "/tmp/energy-platform-podman-storage"
[storage.options]
ignore_chown_errors = "true"
[storage.options.overlay]
mount_program = "/usr/bin/fuse-overlayfs"
EOF
  export CONTAINERS_STORAGE_CONF="$PODMAN_STORAGE_CONF"
}

docker_is_podman_wrapper() {
  local docker_path
  docker_path="$(command -v docker 2>/dev/null || true)"
  [[ -n "$docker_path" ]] && grep -q 'exec /usr/bin/podman' "$docker_path"
}

ensure_container_runtime() {
  if command -v docker >/dev/null 2>&1 && ! docker_is_podman_wrapper; then
    if docker info >/dev/null 2>&1; then
      CONTAINER_RUNTIME="docker"
      return 0
    fi
  fi

  if command -v podman >/dev/null 2>&1; then
    CONTAINER_RUNTIME="podman"
    export DOCKER_HOST="unix:///run/user/$(id -u)/podman/podman.sock"
    configure_podman_storage
    systemctl --user start podman.socket >/dev/null 2>&1 || true
    if podman info >/dev/null 2>&1; then
      return 0
    fi
  fi

  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    CONTAINER_RUNTIME="docker"
    return 0
  fi

  echo "No working container runtime was detected." >&2
  echo "Start Docker Desktop / docker.service, or ensure Podman is installed and usable." >&2
  exit 1
}

ensure_container_runtime

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

echo "Starting Energy Platform containers..."
"${COMPOSE_CMD[@]}" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up --build -d excel-consumption-service client-web

echo
echo "Energy Platform is starting."
WEB_PORT="$(grep '^WEB_PORT=' "$ENV_FILE" | tail -n 1 | cut -d= -f2)"
API_PORT="$(grep '^API_PORT=' "$ENV_FILE" | tail -n 1 | cut -d= -f2)"
echo "Web app:    http://localhost:${WEB_PORT:-4173}"
echo "API:        http://localhost:${API_PORT:-8000}"
echo
echo "Observability services are optional and are not started by default."
echo "Use \`./stop.sh\` to stop the stack."
echo "Use \`./reset.sh --force\` to remove containers, images, volumes, and runtime data."
