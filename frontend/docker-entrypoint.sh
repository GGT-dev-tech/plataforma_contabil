#!/bin/sh
# This script runs at container startup and injects the VITE_API_URL into the built JS
# by creating a runtime config file that the browser loads before the app.

CONFIG_FILE="/usr/share/nginx/html/config.js"

# Use VITE_API_URL from environment, fallback to the production backend URL
API_URL="${VITE_API_URL:-https://backend-production-8502.up.railway.app}"

# Strip trailing slashes
API_URL=$(echo "$API_URL" | sed 's|/*$||')

# Ensure /api/v1 is appended if missing
case "$API_URL" in
  */api/v1) ;;
  *) API_URL="${API_URL}/api/v1" ;;
esac

echo "window.__API_URL__ = '${API_URL}';" > "$CONFIG_FILE"
echo "Injected API URL: ${API_URL}"

# Fix nginx port
sed -i -e "s/listen 80;/listen ${PORT:-80};/g" /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'
