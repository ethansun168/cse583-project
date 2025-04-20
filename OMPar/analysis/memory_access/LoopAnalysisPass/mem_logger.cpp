#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

static FILE *logFile = NULL;
static pthread_mutex_t logMutex = PTHREAD_MUTEX_INITIALIZER;

__attribute__((constructor)) void initLog() {
    logFile = fopen("mem_access_log.txt", "w");
    if (!logFile) {
        fprintf(stderr, "Error opening mem_access_log.txt for writing!\n");
        exit(EXIT_FAILURE);
    }
    fflush(stderr);
}

__attribute__((destructor)) void closeLog() {
    if (logFile) {
        fclose(logFile);
        fflush(stderr);
    }
}

// Updated to take two parameters: the address and the loopId.
extern "C" __attribute__((noinline)) void logMemoryAccessFunc(void *address, int loopId) {
    pthread_mutex_lock(&logMutex);
    if (logFile) {
        fprintf(logFile, "LOG: %p ID: %d\n", address, loopId);
        fflush(logFile);
    }
    fflush(stderr);
    pthread_mutex_unlock(&logMutex);
}
