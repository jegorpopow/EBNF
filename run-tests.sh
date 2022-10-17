#!/bin/bash
set -euo pipefail
[ "$#" -ge 1 ] || (echo "Expected at least one argument: command to run" && exit 1)

FAIL=0
for tn in $(cat "tests/tests.txt"); do
    tin="tests/$tn.in"
    tout="tests/$tn-${1}.out"
    tsol="tests/$tn-${1}.sol"
    echo ===== $tn =====
    { python3 "$1".py $tin $tout && diff $tout $tsol && echo PASS; } || { echo -e "\e[31;1mFAIL\e[0m" && FAIL=1; }
done
if [[ "$FAIL" == "0" ]]; then
    echo -e "===== \e[32;1mALL PASS\e[0m ====="
else
    echo -e "===== \e[31;1mSOME FAIL\e[0m ====="
fi
exit $FAIL
