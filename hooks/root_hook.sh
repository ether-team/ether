#! /bin/bash

cleanup() { rm -f $input; exit $rc; }
trap cleanup 0 2 3 15

input=$(mktemp)
read -t 0 && cat > $input

rc=0
for script in $(find $0.d -executable \( -type l -o -type f \)); do
    $script $@ < $input || rc=$?
done
