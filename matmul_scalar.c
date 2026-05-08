#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>



void matmul_scalar(float *A, float *B, float *C, int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            float sum = 0.0f;
            for (int k = 0; k < n; k++) {
                sum += A[i * n + k] * B[k * n + j];
            }
            C[i * n + j] = sum;
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <matrix_size>\n", argv[0]);
        return 1;
    }
    int n = atoi(argv[1]);
    size_t size = n * n * sizeof(float);

    float *A = (float*)malloc(size);
    float *B = (float*)malloc(size);
    float *C = (float*)calloc(n * n, sizeof(float));

    // 初始化数据
    for (int i = 0; i < n * n; i++) {
        A[i] = (i % 10) + 1.0f;
        B[i] = ((i * 3) % 7) + 1.0f;
    }


    matmul_scalar(A, B, C, n);


    printf("Matmul finished for size %d\n", n);

    free(A); free(B); free(C);
    return 0;
}