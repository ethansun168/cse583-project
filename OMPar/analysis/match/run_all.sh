#!/usr/bin/env bash

# Required configurations
PATH2LIB="$(pwd)/build/LoopAnalysisPass/LoopAnalysisPass.so"
PASS=loop-analysis

# Loop over all database/*/nopragma.c files
for SRC_FILE in ../database_test/*/nopragma.c; do
    [ -e "$SRC_FILE" ] || continue

    DIR_PATH=$(realpath "$(dirname "$SRC_FILE")")
    BENCH_NAME=$(basename "$DIR_PATH")  # folder name, used as base name

    echo "=== Processing $SRC_FILE ==="

    # Create a temporary work directory for compiling
    WORKDIR=$(mktemp -d)
    cp "$SRC_FILE" "$WORKDIR/"
    cd "$WORKDIR"

    # Clean previous outputs
    rm -f default.profraw *_prof *_fplicm *.bc *.profdata *_output *.ll loop_analysis_output.txt mem_access_log.txt

    # Step 1: Generate LLVM bitcode
    clang -emit-llvm -c "nopragma.c" -g -Xclang -disable-O0-optnone -o "${BENCH_NAME}.bc" -Wno-deprecated-non-prototype

    # Step 2: Add PGO instrumentation
    opt -passes='pgo-instr-gen,instrprof' "${BENCH_NAME}.bc" -o "${BENCH_NAME}.prof.bc"

    # Step 3: Link with mem_logger (if used)
    clang -O0 -g -fprofile-instr-generate "${BENCH_NAME}.prof.bc"  -o "${BENCH_NAME}_prof" -lpthread

    # Step 4: Set LLVM profile output file
    export LLVM_PROFILE_FILE="$(pwd)/default.profraw"

    # Step 5: Run instrumented binary to generate profile data
    ./"${BENCH_NAME}_prof" > /dev/null 2>&1

    # Step 6: Merge PGO profile data
    llvm-profdata merge -o "${BENCH_NAME}.profdata" default.profraw

    # Step 7: Apply the PGO profile to the original IR
    opt -passes="pgo-instr-use" -pgo-test-profile-file="${BENCH_NAME}.profdata" -o "${BENCH_NAME}.profdata.bc" < "${BENCH_NAME}.bc"

    # Step 8: Run custom LLVM Loop Analysis Pass (which produces loop_analysis_output.txt)
    opt -load-pass-plugin="$PATH2LIB" -passes="${PASS}" "${BENCH_NAME}.profdata.bc" -o instrumented.bc
    llvm-dis instrumented.bc -o instrumented.ll

    # Step 9: Compile instrumented bitcode
    clang -O0 instrumented.bc  -o "${BENCH_NAME}_instrumented"

    # Step 10: Run instrumented binary (this will trigger our loop logging to file)
    ./"${BENCH_NAME}_instrumented" > /dev/null 2>&1

    # Step 11: Copy custom loop analysis output to the original folder.
    if [ -f loop_analysis_output.txt ]; then
        cp loop_analysis_output.txt "${DIR_PATH}/loop_analysis_output.txt"
        echo "Saved loop_analysis_output.txt to ${DIR_PATH}/"
    else
        echo "loop_analysis_output.txt not generated for ${SRC_FILE}"
    fi

    # Also copy memory access log if it exists.
    if [ -f mem_access_log.txt ]; then
        cp mem_access_log.txt "${DIR_PATH}/memory_access.txt"
        echo "Saved memory_access.txt to ${DIR_PATH}/"
    else
        echo "mem_access_log.txt not generated for ${SRC_FILE}"
    fi

    # Go back and clean up
    cd - > /dev/null
    rm -rf "$WORKDIR"

done

echo "=== All Done ==="