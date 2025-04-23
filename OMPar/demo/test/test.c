#include <stdio.h>
int main() {
    int sum = 0;
//  #pragma omp parallel for reduction( + :sum)
    for (int i = 0; i < 500; i++){
        if (i % 2 == 0) {
            sum += i;
        }
    }
    printf("Sum = %d\n", sum);
    return 0;
}
