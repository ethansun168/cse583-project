#!/usr/bin/env bash

# Required configurations
PATH2LIB="$(pwd)/build/LoopAnalysisPass/LoopAnalysisPass.so"
PASS=loop-analysis
MEM_LOGGER="$(pwd)/mem_logger.o"
CACHE_DIR="$(pwd)/.memlog_cache"
TIMEOUT_LOG="$(pwd)/timeout_log.txt"

# Create cache and log dirs if not exist
mkdir -p "$CACHE_DIR"
echo -n > "$TIMEOUT_LOG"   # clear timeout log

# Compile logging implementation once
clang++ -c -o "$MEM_LOGGER" LoopAnalysisPass/mem_logger.cpp -pthread

# Loop over all database/*/*_nopragma.c files
for SRC_FILE in ../../demo/*/test.c; do
    [ -e "$SRC_FILE" ] || continue

    DIR_PATH=$(realpath "$(dirname "$SRC_FILE")")
    FILENAME=$(basename "$SRC_FILE")
    BENCH_NAME=$(basename "$DIR_PATH")

    # Compute hash of source file content
    FILE_HASH=$(sha256sum "$SRC_FILE" | cut -d ' ' -f1)
    CACHE_LOG="$CACHE_DIR/${FILE_HASH}_memory_access.txt"

    echo "=== Processing $SRC_FILE (hash: $FILE_HASH) ==="

    # Check cache
    # if [ -f "$CACHE_LOG" ]; then
    #     echo "Cache hit for $FILENAME — copying cached result"
    #     cp "$CACHE_LOG" "${DIR_PATH}/memory_access.txt"
    #     continue
    # fi

    # Set up temporary workspace
    WORKDIR=$(mktemp -d)
    cp "$SRC_FILE" "$WORKDIR/"
    cd "$WORKDIR"

    # Clean any previous outputs
    rm -f default.profraw *_prof *_fplicm *.bc *.profdata *_output *.ll words mem_access_log.txt

    # Step 1: Compile to LLVM bitcode
    clang -emit-llvm -c "$FILENAME" -Xclang -disable-O0-optnone -o "${BENCH_NAME}.bc" -Wno-deprecated-non-prototype

    # Step 2: Add PGO instrumentation
    opt -passes='pgo-instr-gen,instrprof' "${BENCH_NAME}.bc" -o "${BENCH_NAME}.prof.bc"

    # Step 3: Link with memory logger
    clang -O0 -g -fprofile-instr-generate "${BENCH_NAME}.prof.bc" "$MEM_LOGGER" -o "${BENCH_NAME}_prof" -lpthread

    # Step 4: Set profile output
    export LLVM_PROFILE_FILE="$(pwd)/default.profraw"

    # Step 5: Run instrumented binary with timeout
    timeout 40s ./"${BENCH_NAME}_prof" > /dev/null 2>&1
    if [ $? -eq 124 ]; then
        echo "⚠️ Timeout during ${BENCH_NAME}_prof execution"
        echo "[prof timeout] $SRC_FILE" >> "$TIMEOUT_LOG"
    fi

    # Step 6: Merge profiling data
    llvm-profdata merge -o "${BENCH_NAME}.profdata" default.profraw

    # Step 7: Apply profile to IR
    opt -passes="pgo-instr-use" -pgo-test-profile-file="${BENCH_NAME}.profdata" -o "${BENCH_NAME}.profdata.bc" < "${BENCH_NAME}.bc"

    # Step 8: Run custom LLVM pass
    opt -load-pass-plugin="$PATH2LIB" -passes="${PASS}" "${BENCH_NAME}.profdata.bc" -o instrumented.bc
    llvm-dis instrumented.bc -o instrumented.ll

    # Step 9: Compile instrumented code
    clang -O0 instrumented.bc "$MEM_LOGGER" -o "${BENCH_NAME}_instrumented"

    # Step 10: Run instrumented binary with timeout
    timeout 40s ./"${BENCH_NAME}_instrumented" > /dev/null 2>&1
    if [ $? -eq 124 ]; then
        echo "⚠️ Timeout during ${BENCH_NAME}_instrumented execution"
        echo "[instrumented timeout] $SRC_FILE" >> "$TIMEOUT_LOG"
    fi

    # Step 11: Save memory access log
    if [ -f mem_access_log.txt ]; then
        cp mem_access_log.txt "$CACHE_LOG"
        cp mem_access_log.txt "${DIR_PATH}/memory_access.txt"
        echo "Saved memory_access.txt to ${DIR_PATH}/"
    else
        echo "mem_access_log.txt not generated for ${SRC_FILE}"
    fi

    # Cleanup
    cd - > /dev/null
    rm -rf "$WORKDIR"
done

echo "=== All Done ==="
echo "Timeouts logged in $TIMEOUT_LOG"
