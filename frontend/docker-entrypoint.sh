#!/bin/sh
set -e
PLACEHOLDER="__NEXT_PUBLIC_API_URL__"
RUNTIME_VALUE="${NEXT_PUBLIC_API_URL:-auto}"
# Replace placeholder in all JS files of the standalone bundle
find /app/.next -type f -name "*.js" -exec \
  sed -i "s|${PLACEHOLDER}|${RUNTIME_VALUE}|g" {} +
exec node server.js "$@"
