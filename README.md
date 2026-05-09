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


# Gem5 Tests

## 文件结构

* configs                   硬件配置文件
* data                      数据文件
  * pic                     图像
  * stats                   原始数据，按照矩阵大小分类
  * gem5_simdata.csv        汇总数据，便于python读取
  * gem5_simdata_proc.py    数据处理与绘图程序
* run_gem5_tests.sh         批量测试脚本 

## configs

硬件系统配置

| Freq | CPU type | CPU core | L1I | L1D | L2 | 内存 | DRAM |
|-------|-------|-------|-------|-------|-------|-------|-------|
| 1GHz | Simple/Minor/O3 | 1 | 32kB | 64kB | 256kB | 512MB | DDR3_1600_8x8 |

根据不同的 CPU type 和缓存层次，加上 gem5 默认配置 SE mode，共7种配置。

## data

数据文件的命名见`gem5_simdata.csv`。

```
# code_id: s = scalar; b = basic; o = outer; t = tiling
# config_type: se = SE; 0s = simple; 0o = o3; 1s = l1simple; 1o = l1o3; 2s = l2simple; 2o = l2o3
```

## 测试脚本

`run_gem5_tests.sh`批量测试所有代码与配置，需要配置参数。命名方式与`gem5_simdata.csv`中定义一致。

```
CONFIG_DIR="configs"                                                # 配置文件目录
BINARY_DIR="/mnt/hgfs/RVV_matmul/rvv_matmul"                        # 测试代码目录
OUTPUT_DIR="/mnt/hgfs/RVV_matmul/rvv_matmul/gem5_test/data/stats"   # 输出文件目录
MATRIX_SIZE="128"                                                   # 矩阵大小参数
```