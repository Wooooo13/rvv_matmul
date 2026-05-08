#include <riscv_vector.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>



void matmul_rvv_basic(float *A, float *B, float *C, int n) {
    memset(C, 0, n * n * sizeof(float));
    for (int i = 0; i < n; i++) {
        for (int k = 0; k < n; k++) {
            float a = A[i * n + k];
            int j = 0;
            while (j < n) {
                size_t vl = __riscv_vsetvl_e32m1(n - j);
                vfloat32m1_t vb = __riscv_vle32_v_f32m1(&B[k * n + j], vl);
                vfloat32m1_t vc = __riscv_vle32_v_f32m1(&C[i * n + j], vl);
                vfloat32m1_t vres = __riscv_vfmacc_vf_f32m1(vc, a, vb, vl);
                __riscv_vse32_v_f32m1(&C[i * n + j], vres, vl);
                j += vl;
            }
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

    for (int i = 0; i < n * n; i++) {
        A[i] = (i % 10) + 1.0f;
        B[i] = ((i * 3) % 7) + 1.0f;
    }

    matmul_rvv_basic(A, B, C, n);


    printf("RVV_basic, finished\n");

    free(A); free(B); free(C);
    return 0;
}