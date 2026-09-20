#! /bin/bash
set -e

CONF_SRC=/code/docker/nginx/household-nginx.conf
HTPASSWD_FILE=/code/docker/nginx/.htpasswd

if grep -q "auth_basic_user_file" "$CONF_SRC" && [ ! -f "$HTPASSWD_FILE" ]; then
  if [ -n "$NGINX_HTPASSWD_CONTENT" ]; then
    printf '%s\n' "$NGINX_HTPASSWD_CONTENT" > "$HTPASSWD_FILE"
    echo "Wrote basic-auth file from NGINX_HTPASSWD_CONTENT"
  else
    echo "WARNING: $HTPASSWD_FILE missing and NGINX_HTPASSWD_CONTENT unset; starting nginx without basic auth"
    grep -v "auth_basic" "$CONF_SRC" > /tmp/household-nginx.conf
    ln -sf /tmp/household-nginx.conf /etc/nginx/sites-enabled/household-nginx.conf
  fi
fi

exec nginx -g 'daemon off;'