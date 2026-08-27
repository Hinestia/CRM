#!/bin/sh
set -e

. "$(dirname "$0")/wait_for_db.sh"

exec "$@"
