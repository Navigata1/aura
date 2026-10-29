# Source in Bash or Zsh. No exports occur until the real-volume preflight passes.
_studio_load_env() {
  local script output
  if [ -n "${BASH_VERSION:-}" ]; then
    script="${BASH_SOURCE[0]}"
  elif [ -n "${ZSH_VERSION:-}" ]; then
    script="${(%):-%x}"
  else
    echo 'studio-env.sh requires Bash or Zsh' >&2
    return 1
  fi
  output="$("${STUDIO_PYTHON:-python3}" "$(dirname "$script")/environment.py")" || return 1
  eval "$output"
}
if _studio_load_env; then
  unset -f _studio_load_env
else
  unset -f _studio_load_env
  return 1 2>/dev/null || exit 1
fi
