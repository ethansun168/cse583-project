#!/bin/bash
# Run static LLVM pass (without profiling data) for Homework 1 EECS 583 Winter 2024.
# This script processes every .c and .cpp file in the input folder.
# For each source file, a temporary LLVM IR is generated, the pass is run,
# and the output is saved in the same folder as the source, always named static.txt.
# The temporary .ll file is deleted after processing.

# Path to the LLVM pass plugin.
PATH2LIB="$(pwd)/build/LoopAnalysisPass/LoopAnalysisPass.so"

# Loop over all .c and .cpp files in the input directory.
for bench in ../../demo/*/test.c; do
    # Skip if no matching file is found.
    if [ ! -e "$bench" ]; then
        continue
    fi

    # Get the directory of the source file and its base name.
    bench_dir=$(dirname "$bench")
    base=$(basename "$bench")
    base="${base%.*}"
    echo "Processing $base from $bench"

    # Remove any previous temporary files (in the current working directory).
    rm -f ml_features.txt *.bc

    # Create a temporary file for the LLVM IR (.ll); it will be removed after processing.
    temp_ll=$(mktemp /tmp/static-XXXX.ll)

    # Compile the source file to LLVM IR and write to the temporary file.
    clang -emit-llvm -S -Xclang -disable-O0-optnone "$bench" -o "$temp_ll"
    if [ $? -ne 0 ]; then
        echo "Error compiling $bench"
        rm -f "$temp_ll"
        continue
    fi

    # Define the output file (static.txt) in the same folder as the source file.
    txt_file="${bench_dir}/static.txt"

    # Run the LLVM pass on the temporary LLVM IR file.
    # The pass output (or error messages) is redirected to static.txt.
    opt -disable-output -load-pass-plugin="$PATH2LIB" -passes="loop-analysis" "$temp_ll" 2> "$txt_file"
    if [ $? -ne 0 ]; then
        echo "Error running the pass on $temp_ll"
        rm -f "$temp_ll"
        continue
    fi

    # If the pass generated ml_features.txt, use it as static.txt.
    if [ -f ml_features.txt ]; then
        mv ml_features.txt "$txt_file"
        echo "Created output file: $txt_file"
    else
        echo "Created output file: $txt_file"
    fi

    # Clean up the temporary LLVM IR file.
    rm -f "$temp_ll"
    rm -f ml_features.txt *.bc
done
