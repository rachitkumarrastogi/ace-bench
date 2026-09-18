# shellcheck shell=bash
# Shared GitHub token loader for DGX/local harvest wrappers.
# Source from other scripts:  # shellcheck source=scripts/_load_github_token.sh
#   source "$(dirname "$0")/_load_github_token.sh" && ace_load_github_token
#
# Never echoes token values — only the path / source label.

ace_token_file_mode() {
  local f="$1"
  if stat -c '%a' "$f" >/dev/null 2>&1; then
    stat -c '%a' "$f"
  elif stat -f '%OLp' "$f" >/dev/null 2>&1; then
    stat -f '%OLp' "$f"
  else
    echo ""
  fi
}

ace_warn_token_perms() {
  local f="$1"
  local mode
  mode="$(ace_token_file_mode "$f")"
  [[ -z "$mode" ]] && return 0
  # Prefer 600: group/other bits should be 0.
  local group other
  group=$((10#$mode / 10 % 10))
  other=$((10#$mode % 10))
  if (( group != 0 || other != 0 )); then
    echo "warning: token file $f mode is $mode (prefer chmod 600)" >&2
  fi
}

ace_load_github_token() {
  local token_file="${TOKEN_FILE:-$HOME/.config/ace-bench/github_token}"
  if [[ -n "${GITHUB_TOKEN:-}" || -n "${GH_TOKEN:-}" ]]; then
    return 0
  fi
  if [[ -f "$token_file" ]]; then
    ace_warn_token_perms "$token_file"
    # Read without printing; strip whitespace only.
    export GITHUB_TOKEN
    GITHUB_TOKEN="$(tr -d '[:space:]' <"$token_file")"
    if [[ -n "$GITHUB_TOKEN" ]]; then
      echo "using token from: $token_file"
      return 0
    fi
    unset GITHUB_TOKEN
  fi
  if command -v gh >/dev/null 2>&1; then
    local tok=""
    if tok="$(gh auth token 2>/dev/null)" && [[ -n "$tok" ]]; then
      export GH_TOKEN="$tok"
      echo "using token from: gh auth token"
      return 0
    fi
  fi
  echo "warning: no token — set GITHUB_TOKEN or write $token_file (mode 600)" >&2
  return 0
}
