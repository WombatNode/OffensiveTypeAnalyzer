#!/bin/sh

cat "$1" | sed -n '/|.*[[:digit:]]/p' |  tr -s ' ' | cut -f3,4 -d'|' | grep '.'