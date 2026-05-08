#include <riscv_vector.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>


void matmul_rvv_outer(float *A, float *B, float *C, int n) {
    // 假设 n 是 VL 的倍数，为了简化逻辑（实际需处理边界）
    for (int i = 0; i < n; i += 4) { // 一次处理 A 的 4 行
        for (int j = 0; j < n; ) {
            size_t vl = __riscv_vsetvl_e32m1(n - j);
            
            // 1. 初始化 C 的 4 个向量寄存器 (对应 C[i...i+3][j...j+vl-1])
            vfloat32m1_t vc0 = __riscv_vfmv_v_f_f32m1(0.0f, vl);
            vfloat32m1_t vc1 = __riscv_vfmv_v_f_f32m1(0.0f, vl);
            vfloat32m1_t vc2 = __riscv_vfmv_v_f_f32m1(0.0f, vl);
            vfloat32m1_t vc3 = __riscv_vfmv_v_f_f32m1(0.0f, vl);

            for (int k = 0; k < n; k++) {
                // 2. 加载 B 的一行段 (B[k][j...j+vl-1])
                vfloat32m1_t vb = __riscv_vle32_v_f32m1(&B[k * n + j], vl);

                // 3. 提取 A 的 4 个标量并做乘累加 (外积核心：A 的列与 B 的行)
                float a0 = A[(i + 0) * n + k];
                float a1 = A[(i + 1) * n + k];
                float a2 = A[(i + 2) * n + k];
                float a3 = A[(i + 3) * n + k];

                vc0 = __riscv_vfmacc_vf_f32m1(vc0, a0, vb, vl);
                vc1 = __riscv_vfmacc_vf_f32m1(vc1, a1, vb, vl);
                vc2 = __riscv_vfmacc_vf_f32m1(vc2, a2, vb, vl);
                vc3 = __riscv_vfmacc_vf_f32m1(vc3, a3, vb, vl);
            }

            // 4. 最后一次性写回内存，避免了 k 循环内的反复读写
            __riscv_vse32_v_f32m1(&C[(i + 0) * n + j], vc0, vl);
            __riscv_vse32_v_f32m1(&C[(i + 1) * n + j], vc1, vl);
            __riscv_vse32_v_f32m1(&C[(i + 2) * n + j], vc2, vl);
            __riscv_vse32_v_f32m1(&C[(i + 3) * n + j], vc3, vl);

            j += vl;
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

    matmul_rvv_outer(A, B, C, n);


    printf("RVV_outer, finished");

    free(A); free(B); free(C);
    return 0;
}