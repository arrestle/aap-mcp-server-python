#!/bin/bash

echo "Removing Podman images older than 30 days..."
podman images --format json | \
  jq -r '.[] | select(.CreatedAtRaw < "'$(date -d '30 days ago' '+%Y-%m-%d %H:%M')'") | .Id' | \
  xargs --no-run-if-empty podman rmi