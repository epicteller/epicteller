#!/usr/bin/env sh
set -e

source "$(poetry env info --path)/bin/activate"

if [ $# -eq 0 ] || [ "${1#-}" != "$1" ]; then
  set -- supervisord "$@"
fi

exec "$@"
