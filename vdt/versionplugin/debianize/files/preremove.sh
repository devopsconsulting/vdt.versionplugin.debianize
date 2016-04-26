#!/bin/sh
set -e

if which pyclean >/dev/null 2>&1; then
pyclean -p <%= name %>
else
	dpkg -L <%= name %> | grep \.py$ | while read file
	do
		rm -f "${file}"[co] >/dev/null
  	done
fi
