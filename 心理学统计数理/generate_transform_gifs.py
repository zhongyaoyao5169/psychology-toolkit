#!/usr/bin/env python3
"""生成方差、标准差、平均数在加常数/乘常数变换下的对比动画。"""

import importlib
import subprocess
import sys


def ensure_packages():
    required = {
        "numpy": "numpy",
        "matplotlib": "matplotlib",
        "seaborn": "seaborn",
        "PIL": "pillow",
    }
    missing = []
    for module, package in required.items():
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(package)
    if missing:
        print(f"正在安装缺失依赖: {', '.join(missing)}")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *missing, "-q"]
        )


ensure_packages()

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation, PillowWriter
import warnings

warnings.filterwarnings("ignore")

plt.rcParams["font.sans-serif"] = [
    "PingFang SC",
    "Hiragino Sans GB",
    "Heiti SC",
    "Microsoft YaHei",
    "SimHei",
    "Arial Unicode MS",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False

OUTPUT_DIR = __import__("pathlib").Path(__file__).resolve().parent

# 与 web/index.template.html 中 modeColor() / modeBoxColor() 一致
MODE_COLORS = {
    "add": "#4A90D9",    # 平移 · 蓝
    "mul": "#3AA984",    # 拉伸 · 绿
    "comb": "#7C7AE0",   # 先乘后加 · 紫
    "comb2": "#E2566B",  # 先加后乘 · 红
}
MODE_BOX_COLORS = {
    "add": "#E3F0FB",
    "mul": "#E8F5EF",
    "comb": "#EEEEF8",
    "comb2": "#FCEEF0",
}
KDE_FILL_ALPHA = 0.35  # 与网页 hexToRgba(color, 0.35) 一致

np.random.seed(42)
X = np.random.normal(loc=50, scale=10, size=200)


def stats_text(y):
    mean = np.mean(y)
    std = np.std(y)
    var = np.var(y)
    return f"均值: {mean:.1f}  标准差: {std:.1f}  方差: {var:.1f}"


def add_mean_std_lines(ax, y):
    mean = np.mean(y)
    std = np.std(y)
    ax.axvline(x=mean, color="red", linestyle="--", linewidth=2, label=f"均值={mean:.1f}")
    ax.axvline(x=mean - std, color="orange", linestyle=":", linewidth=1.5, label="±1标准差")
    ax.axvline(x=mean + std, color="orange", linestyle=":", linewidth=1.5)
    return mean, std


def draw_boxplot(ax, y, mode, title, xlim):
    color = MODE_COLORS[mode]
    fill = MODE_BOX_COLORS[mode]
    ax.boxplot(
        y,
        vert=False,
        widths=0.6,
        patch_artist=True,
        boxprops=dict(facecolor=fill, edgecolor=color, linewidth=1.5),
        medianprops=dict(color=color, linewidth=1.5),
        whiskerprops=dict(color=color, linewidth=1.5),
        capprops=dict(color=color, linewidth=1.5),
        flierprops=dict(markeredgecolor=color, markerfacecolor=fill, alpha=0.8),
    )
    add_mean_std_lines(ax, y)
    ax.set_xlim(*xlim)
    ax.set_ylim(0, 2)
    ax.set_xlabel("数值", labelpad=8)
    ax.set_title(f"{title}\n{stats_text(y)}")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.3)


def draw_kde(ax, y, mode, title, xlim, ylim, show_original=False):
    color = MODE_COLORS[mode]
    sns.kdeplot(y, ax=ax, fill=True, color=color, alpha=KDE_FILL_ALPHA, linewidth=2)
    if show_original:
        sns.kdeplot(
            X,
            ax=ax,
            color="#9A9388",
            linestyle="--",
            linewidth=1.5,
            alpha=0.5,
        )
    add_mean_std_lines(ax, y)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xlabel("数值", labelpad=8)
    ax.set_ylabel("密度")
    ax.set_title(title, pad=28)
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.3)


def save_animation(fig, update_fn, frames, filename):
    ani = FuncAnimation(fig, update_fn, frames=frames, interval=150, repeat=True)
    path = OUTPUT_DIR / filename
    ani.save(path, writer=PillowWriter(fps=8))
    plt.close(fig)
    print(f"✅ 已保存: {path}")
    return path


# 动画1：加常数 C（平移）
fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))


def update_add(frame):
    ax1.clear()
    ax2.clear()
    c = frame * 2
    y = X + c
    draw_boxplot(ax1, y, "add", f"加常数 C = {c:.0f}", (0, 160))
    draw_kde(ax2, y, "add", "核密度曲线（形状完全不变）", (0, 160), (0, 0.06), show_original=True)
    return ax1, ax2


save_animation(fig1, update_add, 51, "平移动画_加常数C.gif")

# 动画2：乘常数 D（拉伸/压缩）
fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))


def update_mul(frame):
    ax1.clear()
    ax2.clear()
    d = 0.5 + frame * 0.05
    y = X * d
    draw_boxplot(ax1, y, "mul", f"乘常数 D = {d:.2f}", (-30, 180))
    draw_kde(
        ax2,
        y,
        "mul",
        "核密度曲线（形状拉伸/压缩）",
        (-30, 180),
        (0, 0.08),
        show_original=True,
    )
    return ax1, ax2


save_animation(fig2, update_mul, 51, "拉伸动画_乘常数D.gif")

# 动画3：组合变换 Y = X×D + C（先乘后加）
fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))


def update_comb(frame):
    ax1.clear()
    ax2.clear()
    d = 0.5 + frame * 0.04
    c = frame * 1.5
    y = X * d + c
    draw_boxplot(ax1, y, "comb", f"Y = X×{d:.2f} + {c:.0f}", (-30, 250))
    draw_kde(
        ax2,
        y,
        "comb",
        "先乘后加：X×D + C",
        (-30, 250),
        (0, 0.08),
        show_original=True,
    )
    return ax1, ax2


save_animation(fig3, update_comb, 51, "组合变换_先乘后加_X乘D加C.gif")

# 动画4：组合变换 Y = (X + C) × D（先加后乘）
fig4, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))


def update_comb2(frame):
    ax1.clear()
    ax2.clear()
    c = frame * 1.5
    d = 0.5 + frame * 0.04
    y = (X + c) * d
    draw_boxplot(ax1, y, "comb2", f"Y = (X + {c:.0f}) × {d:.2f}", (-30, 280))
    draw_kde(
        ax2,
        y,
        "comb2",
        "先加后乘：(X + C) × D",
        (-30, 280),
        (0, 0.08),
        show_original=True,
    )
    return ax1, ax2


save_animation(fig4, update_comb2, 51, "组合变换_先加后乘_X加C乘D.gif")

print("\n🎉 所有 4 种变换动画生成完成！")
