#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
出版级中文封面排版 (7×10 inch，与 6×9 比例一致)
- 书名：云层之上（Noto Serif CJK，大字距 +120~160 pt）
- 副标题、作者、安全边距 0.6 inch、人物区压暗
运行：需安装 matplotlib, numpy；在项目环境中执行 python cover_front_zh.py
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.font_manager as fm

# 7×10 inch, 300 dpi
WIDTH_IN, HEIGHT_IN = 7.0, 10.0
DPI = 300
SAFE_IN = 0.6  # 安全边距

# 颜色 (出版级，非纯黑)
COLOR_TITLE = "#222222"
COLOR_SUBTITLE = "#555555"
COLOR_AUTHOR = "#444444"

# 副标题二选一
SUBTITLE = "一个程序员的山路"
# SUBTITLE = "从山村到硅谷的路"

# 中文字体：用路径避免乱码（FontProperties(fname=...)）
def _get_cjk_fontpaths():
    """返回 (serif_path, sans_path)。优先用 fname= 路径，matplotlib 能正确渲染中文。"""
    serif_path = None
    sans_path = None
    # 1) 从 font_manager 里找已注册的 Noto CJK 字体路径
    for f in fm.fontManager.ttflist:
        path = getattr(f, "fname", None)
        if not path:
            continue
        path = Path(path)
        if not path.exists() or path.suffix.lower() not in (".ttf", ".otf", ".ttc"):
            continue
        s = path.name.lower()
        name = getattr(f, "name", "") or ""
        if "noto serif cjk" in name.lower() or ("noto" in s and "serif" in s and "cjk" in s):
            if not serif_path:
                serif_path = str(path)
        if "noto sans cjk" in name.lower() or ("noto" in s and "sans" in s and "cjk" in s):
            if not sans_path:
                sans_path = str(path)
    # 2) 若没有，再用 findfont 按 family 名解析
    if not serif_path:
        for name in ["Noto Serif CJK SC", "Noto Serif CJK TC", "Source Han Serif CN"]:
            try:
                p = fm.findfont(fm.FontProperties(family=name))
                if p and Path(p).exists():
                    serif_path = p
                    break
            except Exception:
                continue
    if not sans_path:
        for name in ["Noto Sans CJK SC", "Noto Sans CJK TC", "Source Han Sans CN"]:
            try:
                p = fm.findfont(fm.FontProperties(family=name))
                if p and Path(p).exists():
                    sans_path = p
                    break
            except Exception:
                continue
    return serif_path, sans_path


def draw_text_tracked(ax, x, y, text, fontsize, font_path_or_name, weight="normal", color="black", tracking_pt=0, **kwargs):
    """Draw text with letter-spacing. font_path_or_name: path to .ttf/.otf/.ttc (CJK), or font name."""
    if not text:
        return
    pt_to_in = 1.0 / 72.0
    step_in = (fontsize + tracking_pt) * pt_to_in
    x_cur = x - (len(text) - 1) * step_in / 2.0
    use_prop = isinstance(font_path_or_name, (str, Path)) and Path(font_path_or_name).exists()
    for ch in text:
        if use_prop:
            prop = fm.FontProperties(fname=str(font_path_or_name))
            prop.set_size(fontsize)
            prop.set_weight(weight)
            ax.text(x_cur, y, ch, fontproperties=prop, color=color, ha="center", va="center", **kwargs)
        else:
            ax.text(x_cur, y, ch, fontsize=fontsize, fontname=str(font_path_or_name), weight=weight,
                    color=color, ha="center", va="center", **kwargs)
        x_cur += step_in


def dim_image_lower(img, frac_lower=0.35, brightness_factor=0.95, contrast_factor=0.9):
    """对图像下部 (人物区) 做轻微压暗：亮度降约 5%，对比度降约 10%。"""
    h = img.shape[0]
    y_cut = int(h * (1 - frac_lower))
    if img.dtype in (np.float32, np.float64):
        out = img.copy()
    else:
        out = img.astype(np.float64) / 255.0
    mid = 0.5
    block = out[y_cut:, :].copy()
    block = (block - mid) * contrast_factor + mid
    block = np.clip(block * brightness_factor, 0, 1)
    out[y_cut:, :] = block
    if img.dtype not in (np.float32, np.float64):
        out = (np.clip(out, 0, 1) * 255).astype(np.uint8)
    return out


def generate_cover():
    script_dir = Path(__file__).resolve().parent
    bkg_path = script_dir / "cover_front_bkg.png"
    if not bkg_path.exists():
        raise FileNotFoundError(f"Background image not found: {bkg_path}")

    # 中文字体用文件路径，避免乱码
    serif_path, sans_path = _get_cjk_fontpaths()
    if not serif_path or not sans_path:
        # fallback: 全局设置宋体/黑体，部分环境有效
        import matplotlib as mpl
        mpl.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "SimHei", "DejaVu Sans"]
        mpl.rcParams["font.serif"] = ["Noto Serif CJK SC", "SimSun", "DejaVu Serif"]
        mpl.rcParams["axes.unicode_minus"] = False
        serif_path = serif_path or "DejaVu Serif"
        sans_path = sans_path or "DejaVu Sans"

    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(0, WIDTH_IN)
    ax.set_ylim(0, HEIGHT_IN)

    # 背景图 (铺满)
    img = mpimg.imread(str(bkg_path))
    # 可选：人物区压暗，让标题更突出
    img = dim_image_lower(img, frac_lower=0.35, brightness_factor=0.95, contrast_factor=0.9)
    ax.imshow(img, extent=[0, WIDTH_IN, 0, HEIGHT_IN], aspect="auto", zorder=0)

    cx = WIDTH_IN / 2.0

    # 标题区：距顶部约 28%
    title_y = HEIGHT_IN - SAFE_IN - 0.28 * (HEIGHT_IN - 2 * SAFE_IN)
    title_fontsize = 120
    draw_text_tracked(ax, cx, title_y, "云层之上", title_fontsize, serif_path, weight="bold",
                     color=COLOR_TITLE, tracking_pt=140, zorder=2)
    # 副标题：标题下方约 40–50 px
    subtitle_y = title_y - title_fontsize / 72.0 - 50.0 / DPI
    if isinstance(sans_path, (str, Path)) and Path(sans_path).exists():
        prop = fm.FontProperties(fname=str(sans_path), size=30)
        ax.text(cx, subtitle_y, SUBTITLE, fontproperties=prop, color=COLOR_SUBTITLE,
                ha="center", va="center", zorder=2)
    else:
        ax.text(cx, subtitle_y, SUBTITLE, fontsize=30, fontname=str(sans_path), weight="normal",
                color=COLOR_SUBTITLE, ha="center", va="center", zorder=2)

    # 作者：封面高度约 63% 处（从下往上）
    author_y = HEIGHT_IN * 0.63
    draw_text_tracked(ax, cx, author_y, "玄心 著", 38, sans_path, weight="normal",
                      color=COLOR_AUTHOR, tracking_pt=80, zorder=2)

    for ext in ["png", "pdf"]:
        out = script_dir / f"cover_front_zh.{ext}"
        fig.savefig(out, dpi=DPI, bbox_inches=None, pad_inches=0)
        print(f"Saved: {out}")

    plt.close(fig)


if __name__ == "__main__":
    generate_cover()
