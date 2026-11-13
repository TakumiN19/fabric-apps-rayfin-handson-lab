#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=versions.env
source "${SCRIPT_DIR}/versions.env"

readonly MARKETPLACE_PARENT="${XDG_DATA_HOME:-${HOME}/.local/share}/fabric-apps-rayfin-handson-lab"
readonly FABRIC_MARKETPLACE_DIR="${MARKETPLACE_PARENT}/skills-for-fabric-${FABRIC_SKILLS_TAG}"
readonly RAYFIN_MARKETPLACE_DIR="${MARKETPLACE_PARENT}/rayfin-${RAYFIN_SKILLS_COMMIT:0:12}"

failures=0

pass() {
  printf '[OK]   %s\n' "$*"
}

fail() {
  printf '[FAIL] %s\n' "$*" >&2
  failures=$((failures + 1))
}

check_command() {
  local command_name="$1"
  if command -v "${command_name}" >/dev/null 2>&1; then
    pass "${command_name}: $(command -v "${command_name}")"
  else
    fail "${command_name}: command not found"
  fi
}

check_version() {
  local label="$1"
  local expected="$2"
  local actual="$3"

  if [[ "${actual}" == "${expected}" ]]; then
    pass "${label}: ${actual}"
  else
    fail "${label}: expected ${expected}, got ${actual:-<empty>}"
  fi
}

for required_command in \
  python3 node npm npx az copilot rayfin func powerbi-report-author sqlcmd \
  git curl jq bzip2 sudo tar sha256sum awk grep; do
  check_command "${required_command}"
done

if command -v python3 >/dev/null 2>&1; then
  actual="$(python3 -c 'import platform; print(platform.python_version())' 2>/dev/null || true)"
  check_version "Python" "${PYTHON_VERSION}" "${actual}"
fi

if command -v node >/dev/null 2>&1; then
  actual="$(node --version 2>/dev/null || true)"
  check_version "Node.js" "${NODE_VERSION}" "${actual#v}"
fi

if command -v npm >/dev/null 2>&1; then
  actual="$(npm --version 2>/dev/null || true)"
  check_version "npm" "${NPM_VERSION}" "${actual}"
fi

if command -v az >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
  actual="$(az version --output json 2>/dev/null | jq -r '."azure-cli" // ""' || true)"
  check_version "Azure CLI" "${AZURE_CLI_VERSION}" "${actual}"
fi

if command -v copilot >/dev/null 2>&1; then
  actual="$(
    copilot --version 2>/dev/null |
      awk '/^GitHub Copilot CLI / { version=$4; sub(/\.$/, "", version); print version; exit }' ||
      true
  )"
  check_version "GitHub Copilot CLI" "${COPILOT_CLI_VERSION}" "${actual}"
fi

if command -v rayfin >/dev/null 2>&1; then
  actual="$(
    rayfin --version 2>/dev/null |
      awk '/^[0-9]+\.[0-9]+\.[0-9]+/ { print $1; exit }' ||
      true
  )"
  check_version "Rayfin CLI" "${RAYFIN_CLI_VERSION}" "${actual}"
fi

if command -v func >/dev/null 2>&1; then
  actual="$(func --version 2>/dev/null | head -n 1 | tr -d '[:space:]' || true)"
  check_version "Azure Functions Core Tools" "${AZURE_FUNCTIONS_CORE_TOOLS_VERSION}" "${actual}"
fi

if command -v powerbi-report-author >/dev/null 2>&1; then
  actual="$(powerbi-report-author --version 2>/dev/null || true)"
  check_version "Power BI report authoring CLI" "${POWERBI_AUTHORING_CLI_VERSION}" "${actual}"
fi

if command -v sqlcmd >/dev/null 2>&1; then
  actual="$(
    sqlcmd --version 2>/dev/null |
      awk '/^Version:/ { version=$2; sub(/^v/, "", version); print version; exit }' ||
      true
  )"
  check_version "go-sqlcmd" "${SQLCMD_VERSION}" "${actual}"
fi

if [[ -d "${FABRIC_MARKETPLACE_DIR}/.git" ]]; then
  actual="$(git -C "${FABRIC_MARKETPLACE_DIR}" rev-parse HEAD 2>/dev/null || true)"
  check_version "skills-for-fabric commit" "${FABRIC_SKILLS_COMMIT}" "${actual}"
else
  fail "skills-for-fabric checkout not found: ${FABRIC_MARKETPLACE_DIR}"
fi

if [[ -d "${RAYFIN_MARKETPLACE_DIR}/.git" ]]; then
  actual="$(git -C "${RAYFIN_MARKETPLACE_DIR}" rev-parse HEAD 2>/dev/null || true)"
  check_version "microsoft/rayfin commit" "${RAYFIN_SKILLS_COMMIT}" "${actual}"
else
  fail "microsoft/rayfin checkout not found: ${RAYFIN_MARKETPLACE_DIR}"
fi

if command -v copilot >/dev/null 2>&1; then
  plugin_list="$(copilot plugin list 2>/dev/null || true)"
  if grep -Fq "fabric-skills@fabric-collection (v${FABRIC_SKILLS_VERSION})" <<<"${plugin_list}"; then
    pass "fabric-skills plugin: v${FABRIC_SKILLS_VERSION}"
  else
    fail "fabric-skills plugin: expected v${FABRIC_SKILLS_VERSION}"
  fi

  if grep -Fq "powerbi-authoring@fabric-collection (v${FABRIC_SKILLS_VERSION})" <<<"${plugin_list}"; then
    pass "powerbi-authoring plugin: v${FABRIC_SKILLS_VERSION}"
  else
    fail "powerbi-authoring plugin: expected v${FABRIC_SKILLS_VERSION}"
  fi

  if grep -Fq "rayfin@rayfin-skills (v${RAYFIN_SKILLS_VERSION})" <<<"${plugin_list}"; then
    pass "rayfin plugin: v${RAYFIN_SKILLS_VERSION}"
  else
    fail "rayfin plugin: expected v${RAYFIN_SKILLS_VERSION}"
  fi
fi

if ((failures > 0)); then
  printf '\nEnvironment verification failed with %d issue(s).\n' "${failures}" >&2
  exit 1
fi

printf '\nEnvironment verification completed successfully.\n'
