CONFIG_DIR="configs"
BINARY_DIR="/mnt/hgfs/RVV_matmul/rvv_matmul"
OUTPUT_DIR="/mnt/hgfs/RVV_matmul/rvv_matmul/gem5_test/data/stats"
MATRIX_SIZE="512"

declare -A VERSIONS=(
    [s]="matmul_scalar"
    [b]="matmul_rvv_basic"
    [o]="matmul_rvv_outer"
    [t]="matmul_rvv_tiling"
)

declare -A CONFIGS=(
    [se]="$CONFIG_DIR/deprecated/example/se.py"
    [0s]="$CONFIG_DIR/rvv_matmul/mysimplecpu.py"
    [0o]="$CONFIG_DIR/rvv_matmul/myo3cpu.py"
    [1s]="$CONFIG_DIR/rvv_matmul/myL1simplecpu.py"
    [1o]="$CONFIG_DIR/rvv_matmul/myL1o3cpu.py"
    [2s]="$CONFIG_DIR/rvv_matmul/myL2simplecpu.py"
    [2o]="$CONFIG_DIR/rvv_matmul/myL2o3cpu.py"
)

for config_type in "${!CONFIGS[@]}"; do
    config_path="${CONFIGS[$config_type]}"
    
    for code_id in "${!VERSIONS[@]}"; do
        binary_name="${VERSIONS[$code_id]}"
        binary_path="$BINARY_DIR/$binary_name"
        
        ./build/RISCV/gem5.opt "$config_path" \
            -c "$binary_path" \
            -o "$MATRIX_SIZE"
        
        if [ -f "m5out/stats.txt" ]; then
            filename="stats_${code_id}_${config_type}.txt"
            cp m5out/stats.txt "$OUTPUT_DIR/$filename"
            rm -rf m5out
        fi
    done
done

echo "========== 所有测试完成 =========="