# rvv_matmul
编译：
```
riscv64-unknown-elf-gcc -march=rv64gc -O2 -fno-tree-vectorize matmul_scalar.c -o matmul_scalar
riscv64-unknown-elf-gcc -march=rv64gcv -mabi=lp64d -O2 matmul_rvv_basic.c -o matmul_rvv_basic
riscv64-unknown-elf-gcc -march=rv64gcv -mabi=lp64d -O2 matmul_rvv_outer.c -o matmul_rvv_outer
riscv64-unknown-elf-gcc -march=rv64gcv -mabi=lp64d -O2 matmul_rvv_tiling.c -o matmul_rvv_tiling
```
运行, N = 16 32 64 128 512
```
spike --isa=rv64gcv pk matmul_scalar/matmul_rvv_basic/matmul_rvv_outer/matmul_rvv_tiling N
```

matmul_scalar.c 标准三重循环矩阵乘积
matmul_rvv_basic.c 标准三重循环改成向量版
matmul_rvv_outer.c 矩阵外积
matmul_rvv_tiling.c 分块矩阵
