#!/bin/bash

CONFIG_DIR="$1"
file="/tmp/state.json"

[ "${DEBUG}" = 'true' ] && set -x

./bin/folder_to_consul_json.py from-folders "${CONFIG_DIR}" "${file}" &&
  consul kv import "@${file}" &&
  rm "${file}"
