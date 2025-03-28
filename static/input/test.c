#include <stdio.h>

#define MAX 20
#define LIMIT 10000

int main() {
    int fib[MAX];
    int i, sum_even = 0;

    // Initialize first two Fibonacci numbers
    fib[0] = 0;
    fib[1] = 1;

    // Generate Fibonacci sequence
    for (i = 2; i < MAX; i++) {
        fib[i] = fib[i - 1] + fib[i - 2];
    }

    // Calculate sum of even Fibonacci numbers below LIMIT
    for (i = 0; i < MAX; i++) {
        if (fib[i] > LIMIT) {
            break;
        }
        if (fib[i] % 2 == 0) {
            sum_even += fib[i];
        }
    }

    // At this point, fib[] holds the sequence and sum_even holds the result
    // You could print them if needed, but skipping it as you requested

    return 0;
}
