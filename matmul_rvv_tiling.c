#include <riscv_vector.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define BLK 32


void matmul_rvv_tiling(float *A, float *B, float *C, int n) {
    memset(C, 0, n * n * sizeof(float));
    // 调整循环顺序为 i0 -> k0 -> j0，提升B矩阵的缓存命中率
    for (int i0 = 0; i0 < n; i0 += BLK) {
        int i_end = (i0 + BLK < n) ? i0 + BLK : n;
        for (int k0 = 0; k0 < n; k0 += BLK) {
            int k_end = (k0 + BLK < n) ? k0 + BLK : n;
            for (int j0 = 0; j0 < n; j0 += BLK) {
                int j_end = (j0 + BLK < n) ? j0 + BLK : n;
                for (int i = i0; i < i_end; i++) {
                    int j = j0;
                    while (j < j_end) {
                        size_t vl = __riscv_vsetvl_e32m1(j_end - j);
                        // 核心修正：将C的加载移到k循环之外！
                        vfloat32m1_t vc = __riscv_vle32_v_f32m1(&C[i * n + j], vl);
                        // 在k分块内，仅在寄存器内累加，不写回内存
                        for (int k = k0; k < k_end; k++) {
                            float a = A[i * n + k];
                            vfloat32m1_t vb = __riscv_vle32_v_f32m1(&B[k * n + j], vl);
                            vc = __riscv_vfmacc_vf_f32m1(vc, a, vb, vl);
                        }
                        // k分块累加结束后，一次性写回内存
                        __riscv_vse32_v_f32m1(&C[i * n + j], vc, vl);
                        j += vl;
                    }
                }
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


    matmul_rvv_tiling(A, B, C, n);


    printf("RVV_tiling, finished\n");

    free(A); free(B); free(C);
    return 0;
}