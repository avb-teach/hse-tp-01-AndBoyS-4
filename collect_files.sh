#!/bin/bash
# need to install getopt on Mac for --max_depth to work

max_depth="0"
in=$1
out=$2

TEMP=$(getopt -o vdm: --long max_depth: \
              -n 'javawrap' -- "$@")

if [ $? != 0 ] ; then echo "Terminating..." >&2 ; exit 1 ; fi

# Note the quotes around '$TEMP': they are essential!
eval set -- "$TEMP"

while true; do
  case "$1" in
    --max_depth )
      echo $2; max_depth=$2; break;;
    -- ) shift; break ;;
    * ) break ;;
  esac
done

uv run scripts/collect_files.py "$in" "$out" "$max_depth"
