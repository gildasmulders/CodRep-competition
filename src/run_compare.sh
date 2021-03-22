#! /bin/bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR="$(dirname "$CURRENT_DIR")"
NEW_DIR="New_datasets"

if [ ! -f $CURRENT_DIR/compare2.out ]; then
    python3 $CURRENT_DIR/compare.py --src $ROOT_DIR/../SequenceR/results/Golden/src-val.txt $ROOT_DIR/../SequenceR/results/Golden/src-train.txt $ROOT_DIR/../SequenceR/results/Golden/src-test.txt --rebuilt $ROOT_DIR/$NEW_DIR/Dataset3/abstractions.txt $ROOT_DIR/$NEW_DIR/Dataset1/abstractions.txt $ROOT_DIR/$NEW_DIR/Dataset2/abstractions.txt $ROOT_DIR/$NEW_DIR/Dataset5/abstractions.txt $ROOT_DIR/$NEW_DIR/Dataset4/abstractions.txt > $CURRENT_DIR/compare2.out
fi

cat $CURRENT_DIR/compare2.out