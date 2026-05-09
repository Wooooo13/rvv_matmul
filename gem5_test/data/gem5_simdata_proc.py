import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": "Times New Roman",
        "font.size": 9,
        "axes.labelsize": 9,
        "axes.titlesize": 9,
        "legend.fontsize": 9,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
    }
)
plt.rcParams["axes.unicode_minus"] = False


class Gem5DataProcessor:
    def __init__(self, csv_file):
        """初始化数据处理器"""
        self.csv_file = csv_file
        self.df = pd.read_csv(csv_file, comment="#")
        print(f"✓ 加载数据: {csv_file}")
        print(f"  行数: {len(self.df)}")

    def get_metric_by_code(self, metric, matrix_size=128):
        """按代码版本获取指定指标的数据"""
        filtered = self.df[
            (self.df["matrix_size"] == matrix_size) & (self.df["test_metric"] == metric)
        ]
        return filtered.sort_values("code_id")

    def plot_all_metrics(self, matrix_size=128):
        """绘制所有指标的对比图"""
        metrics = self.df["test_metric"].unique()

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()

        code_map = {
            "s": "Scalar",
            "b": "RVV Basic",
            "o": "RVV Outer",
            "t": "RVV Tiling",
        }
        metric_names = {
            "c": "CPU Cycles",
            "i": "Instructions",
            "ipc": "IPC",
            "simt": "Simulated Time",
        }
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A"]

        for idx, metric in enumerate(sorted(metrics)):
            data = self.get_metric_by_code(metric, matrix_size)

            if data.empty:
                continue

            ax = axes[idx]
            codes = [code_map.get(c, c) for c in data["code_id"]]
            values = data["value"].values

            bars = ax.bar(
                codes, values, color=colors, edgecolor="black", linewidth=1.2, alpha=0.8
            )

            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{int(height):,}" if height > 100 else f"{height:.2f}",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    fontweight="bold",
                )

            ax.set_title(
                metric_names.get(metric, metric), fontsize=11, fontweight="bold"
            )
            ax.set_ylabel("Value", fontsize=10)
            ax.grid(axis="y", alpha=0.3, linestyle="--")
            ax.set_axisbelow(True)

        # 隐藏未使用的子图
        for idx in range(len(metrics), len(axes)):
            axes[idx].set_visible(False)

        plt.suptitle(
            f"Gem5 Performance Metrics - Matrix {matrix_size}×{matrix_size}",
            fontsize=14,
            fontweight="bold",
            y=1.00,
        )
        plt.tight_layout()

        return fig

    def plot_dual_metrics(self, metric1, metric2, matrix_size=128, figsize=(7, 4)):
        """绘制双指标对比图 - 每个代码对应两个柱子"""
        data1 = self.get_metric_by_code(metric1, matrix_size)
        data2 = self.get_metric_by_code(metric2, matrix_size)

        if data1.empty or data2.empty:
            print(f"✗ 未找到数据")
            return

        code_map = {
            "s": "Scalar",
            "b": "RVV Basic",
            "o": "RVV Outer",
            "t": "RVV Tiling",
        }

        metric_names = {
            "c": "CPU Cycles",
            "i": "Instructions",
            "ipc": "IPC",
            "simt": "Simulated Time",
        }

        # 按指定顺序排序数据
        code_order = ["s", "b", "o", "t"]
        data1 = data1.set_index("code_id").loc[code_order].reset_index()
        data2 = data2.set_index("code_id").loc[code_order].reset_index()

        # 提取数据
        codes = [code_map.get(c, c) for c in data1["code_id"]]
        values1 = data1["value"].values
        values2 = data2["value"].values

        # 创建图表 - 加大宽度
        fig, ax = plt.subplots(figsize=figsize, dpi=300)

        x = np.arange(len(codes)) * 1.5  # 加大间距：原来是 np.arange(len(codes))
        width = 0.65  # 柱宽

        # 绘制两组柱子 - 去掉黑框
        color_primary = "#1f77b4"
        bars1 = ax.bar(
            x - width / 2,
            values1,
            width=width,
            color=color_primary,
            edgecolor="none",
            linewidth=0,
            alpha=0.8,
            label=metric_names.get(metric1, metric1),
        )

        color_secondary = "#2ca02c"
        bars2 = ax.bar(
            x + width / 2,
            values2,
            width=width,
            color=color_secondary,
            edgecolor="none",
            linewidth=0,
            alpha=0.8,
            label=metric_names.get(metric2, metric2),
        )

        # 标注数值
        for bar in bars1:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{int(height):,}" if height > 100 else f"{height:.2f}",
                ha="center",
                va="bottom",
                fontsize=9,
                color=color_primary,
            )

        for bar in bars2:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{int(height):,}" if height > 100 else f"{height:.2f}",
                ha="center",
                va="bottom",
                fontsize=9,
                color=color_secondary,
            )

        # 标签和格式
        ax.set_xticks(x)
        ax.set_xticklabels(codes, rotation=0, fontsize=9)
        ax.set_ylabel("Value", fontsize=9)
        ax.set_xlabel("Code Version", fontsize=9)
        ax.set_title(
            f"{metric_names.get(metric1, metric1)} & {metric_names.get(metric2, metric2)} - "
            f"Matrix {matrix_size}×{matrix_size}",
            fontsize=10,
            fontweight="bold",
            pad=25,
        )

        # 网格
        ax.grid(axis="y", alpha=0.3, linestyle="--")
        ax.set_axisbelow(True)

        # 图例 - 去掉框
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.10),
            ncol=2,
            frameon=False,
            fontsize=9,
        )

        # 调整布局
        fig.subplots_adjust(left=0.1, right=0.9, bottom=0.07, top=0.92)

        return fig, ax

    def calculate_speedup(self, baseline="s", matrix_size=128):
        """计算相对于基准版本的加速比"""
        print(f"\n=== 加速比分析 (相对于 {baseline}) ===")

        # 获取 CPU Cycles 数据
        cycles_data = self.get_metric_by_code("c", matrix_size)
        baseline_cycles = cycles_data[cycles_data["code_id"] == baseline][
            "value"
        ].values

        if len(baseline_cycles) == 0:
            print(f"✗ 未找到基准版本数据: {baseline}")
            return

        baseline_cycles = baseline_cycles[0]

        code_map = {
            "s": "Scalar",
            "b": "RVV Basic",
            "o": "RVV Outer",
            "t": "RVV Tiling",
        }

        for _, row in cycles_data.iterrows():
            code_id = row["code_id"]
            cycles = row["value"]
            speedup = baseline_cycles / cycles
            reduction = (1 - cycles / baseline_cycles) * 100

            print(
                f"  {code_map.get(code_id, code_id):12s}: {speedup:.2f}x speedup ({reduction:+.1f}% cycles)"
            )


# 主程序
if __name__ == "__main__":
    # 初始化处理器
    processor = Gem5DataProcessor("gem5_simdata.csv")

    # 计算加速比
    processor.calculate_speedup(baseline="s")

    # 绘制所有指标
    fig3 = processor.plot_all_metrics(matrix_size=128)
    plt.savefig("pic/all_metrics_comparison.png", dpi=300, bbox_inches="tight")
    print("✓ 保存: all_metrics_comparison.png")

    # 绘制双指标合并图
    fig4, ax4 = processor.plot_dual_metrics("c", "i", matrix_size=128)
    plt.savefig("pic/cycles_instructions_dual.png", dpi=300, bbox_inches="tight")
    print("✓ 保存: cycles_instructions_dual.png")

    plt.show()
