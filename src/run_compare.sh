#! /bin/bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR="$(dirname "$CURRENT_DIR")"

if [ ! -f $CURRENT_DIR/compare.out ]; then
    python3 $CURRENT_DIR/compare.py --src $ROOT_DIR/../SequenceR/results/Golden/src-val.txt $ROOT_DIR/../SequenceR/results/Golden/src-train.txt $ROOT_DIR/../SequenceR/results/Golden/src-test.txt --rebuilt $ROOT_DIR/Truncated_Abstract_buggy_contexts/Dataset3/abstractions.txt $ROOT_DIR/Truncated_Abstract_buggy_contexts/Dataset1/abstractions.txt $ROOT_DIR/Truncated_Abstract_buggy_contexts/Dataset2/abstractions.txt $ROOT_DIR/Truncated_Abstract_buggy_contexts/Dataset5/abstractions.txt $ROOT_DIR/Truncated_Abstract_buggy_contexts/Dataset4/abstractions.txt > $CURRENT_DIR/compare.out
fi

cat $CURRENT_DIR/compare.out