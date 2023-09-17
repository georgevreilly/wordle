#!/bin/bash

for i in {3..6}; do
    echo wordle${i};
    ./wordle${i}.py "$@"
done
