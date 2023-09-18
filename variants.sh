#!/bin/bash

#VARIANTS=(3 4 5 6)
VARIANTS=(6 8)
for i in "${VARIANTS[@]}"; do
    echo wordle${i};
    ./wordle${i}.py "$@"
done
