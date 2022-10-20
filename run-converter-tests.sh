#!/bin/bash
set -euo pipefail

FAIL=0
for tn in $(cat "tests/tests.txt"); do
    tin="tests/$tn.in"
    tout="tests/$tn-converter.out"
    trout="tests/$tn-converter-readable.out"
    { python3 converter.py $tin $tout; } || { echo -e "\e[31;1mFAIL\e[0m" && FAIL=1; }
    { python3 converter.py -r $tin $trout; } || { echo -e "\e[31;1mFAIL\e[0m" && FAIL=1; }
done

if [[ "$FAIL" == "0" ]]; then
    echo -e "===== \e[32;1mALL PASS\e[0m ====="
else
    echo -e "===== \e[31;1mSOME FAIL\e[0m ====="
fi
exit $FAIL
