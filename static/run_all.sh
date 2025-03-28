
#!/bin/bash
# Run script for Homework 1 EECS 583 Winter 2024
# This script processes all .c and .cpp files in the src folder
# and runs the LLVM pass without using any profiling data.
# For each source file, it creates an output file named <basename>.txt.

# Path to your LLVM pass plugin and the pass name.
PATH2LIB="./build/LoopAnalysisPass/LoopAnalysisPass.so"

# Clean up any previous run files.
rm -f ml_features.txt *.bc

# Loop over all .c and .cpp files in the src directory.
for bench in input/*.c input/*.cpp; do
    # Skip if no matching file is found.
    if [ ! -e "$bench" ]; then
        continue
    fi

    # Extract the base name (without extension) for output naming.
    base=$(basename "$bench")
    base="${base%.*}"
    echo "Processing $base from $bench"

    # Remove any previous temporary files.
    rm -f ml_features.txt *.bc

    # Compile the source file to LLVM IR (.ll file).
    clang -emit-llvm -S -Xclang -disable-O0-optnone "$bench" -o "${base}.ll"
    if [ $? -ne 0 ]; then
        echo "Error compiling $bench"
        continue
    fi

    # 2. Run your LLVM pass on the bitcode file.
    opt -disable-output -load-pass-plugin="$PATH2LIB" -passes="loop-analysis" "${base}.ll" 2> "${base}.txt"
    if [ $? -ne 0 ]; then
        echo "Error running the pass on ${base}.ll"
        continue
    fi

    # 3. Rename the output file (ml_features.txt) to <basename>.txt.
    if [ -f ml_features.txt ]; then
        mv ml_features.txt "${base}.txt"
        echo "Created output file: ${base}.txt"
    else
        echo "Warning: ml_features.txt was not generated for $base"
    fi

    # Cleanup temporary files.
    rm -f ml_features.txt *.bc
done
