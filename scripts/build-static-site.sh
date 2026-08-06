#!/bin/sh
set -eu

rm -rf public
mkdir -p public

find . -maxdepth 1 -type f -name "*.html" -exec cp {} public/ \;

if [ -d assets ]; then
  cp -R assets public/assets
fi

if [ -d dossiers ]; then
  cp -R dossiers public/dossiers
fi
