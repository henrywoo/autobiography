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
COLOR_TITLE = "#000000"
COLOR_SUBTITLE1 = "#111111"
COLOR_SUBTITLE2 = "#fefefe"
COLOR_AUTHOR = "#222222"

# 副标题（可换）
SUBTITLE = "从泥土到云端的修行"
SUBTITLE = "从大山泉水到硅谷AI的生命行路"
SUBTITLE = "在智能之巅  望故乡的泉"
# SUBTITLE = "从泥土到云端的行路"
# SUBTITLE = "一条通向云层的山路"
# SUBTITLE = "山、路、与云"

# 可选：英文书名（None 则不显示）
SUBTITLE_EN = "Above the Clouds"
# 可选：体裁说明（None 则不显示）
GENRE_LINE = "关于成长与时代的\n自传体纪实散文"

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


def dim_image_lower(img, frac_lower=0.35, brightness_factor=0.95, contrast_factor=0.9, blend_frac=0.08):
    """对图像下部 (人物区) 压暗，上缘渐变过渡；仅处理 RGB，保留 alpha。"""
    h = img.shape[0]
    y_cut = int(h * (1 - frac_lower))
    if img.dtype in (np.float32, np.float64):
        out = img.copy()
    else:
        out = img.astype(np.float64) / 255.0
    # 只压暗 RGB，RGBA 时保留 alpha；灰度图压暗整幅
    mid = 0.5
    n_lower = h - y_cut
    blend_rows = max(1, int(n_lower * blend_frac))  # 上缘渐变行数
    if out.ndim == 2:
        for row in range(y_cut, h):
            t = (row - y_cut) / blend_rows if row - y_cut < blend_rows else 1.0
            blend_orig = 1.0 - t
            block = out[row, :].copy()
            dimmed = (block - mid) * contrast_factor + mid
            dimmed = np.clip(dimmed * brightness_factor, 0, 1)
            out[row, :] = blend_orig * block + (1 - blend_orig) * dimmed
    else:
        rgb_end = 3 if out.shape[2] >= 3 else out.shape[2]
        for row in range(y_cut, h):
            t = (row - y_cut) / blend_rows if row - y_cut < blend_rows else 1.0
            blend_orig = 1.0 - t
            block = out[row, :, :rgb_end].copy()
            dimmed = (block - mid) * contrast_factor + mid
            dimmed = np.clip(dimmed * brightness_factor, 0, 1)
            out[row, :, :rgb_end] = blend_orig * block + (1 - blend_orig) * dimmed
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

    # 背景图：调低 alpha 让标题更突出
    img = mpimg.imread(str(bkg_path))
    img = dim_image_lower(img, frac_lower=0.35, brightness_factor=0.95, contrast_factor=0.9)
    ax.imshow(img, extent=[0, WIDTH_IN, 0, HEIGHT_IN], aspect="auto", alpha=0.75, zorder=0)

    cx = WIDTH_IN / 2.0

    # 标题区：略下移，与人物/山顶视觉更融合，有「站在云上」感
    title_y = HEIGHT_IN - SAFE_IN - 0.19 * (HEIGHT_IN - 2 * SAFE_IN)
    title_fontsize = 64
    # 字距缩小使四字不超出页面：(fontsize+tracking)*3/72 约 ≤ 7-2*0.6 ≈ 5.8 inch
    tracking_pt = 20
    draw_text_tracked(ax, cx, title_y, "云层之上", title_fontsize, serif_path, weight="bold",
                     color=COLOR_TITLE, tracking_pt=tracking_pt, zorder=2)
    # 副标题
    subtitle_y = title_y - title_fontsize / 72.0 - 10.0 / DPI
    subtitle_fontsize = 24
    if isinstance(sans_path, (str, Path)) and Path(sans_path).exists():
        prop = fm.FontProperties(fname=str(sans_path), size=subtitle_fontsize)
        ax.text(cx, subtitle_y, SUBTITLE, fontproperties=prop, color=COLOR_SUBTITLE1,
                ha="center", va="center", zorder=2)
    else:
        ax.text(cx, subtitle_y, SUBTITLE, fontsize=subtitle_fontsize, fontname=str(sans_path), weight="normal",
                color=COLOR_SUBTITLE1, ha="center", va="center", zorder=2)

    # 英文书名（可选）
    next_y = subtitle_y - subtitle_fontsize / 72.0 - 14.0 / DPI
    if SUBTITLE_EN:
        en_fontsize = 16
        ax.text(cx, next_y, SUBTITLE_EN, fontsize=en_fontsize, fontname="DejaVu Sans",
                fontstyle="italic", color=COLOR_SUBTITLE1, ha="center", va="center", zorder=2)
        next_y = next_y - en_fontsize / 72.0 - 20.0 / DPI
    else:
        next_y = next_y - 20.0 / DPI

    # 作者
    author_y = next_y - 100.0 / DPI
    draw_text_tracked(ax, cx, author_y, "玄心•著", 24, sans_path, weight="normal",
                      color=COLOR_AUTHOR, tracking_pt=0, zorder=2)

    # 体裁说明（可选，封面底部小字）
    if GENRE_LINE:
        genre_y = SAFE_IN + 0.35
        genre_fontsize = 13
        if isinstance(sans_path, (str, Path)) and Path(sans_path).exists():
            prop_genre = fm.FontProperties(fname=str(sans_path), size=genre_fontsize)
            ax.text(cx, genre_y, GENRE_LINE, fontproperties=prop_genre, color=COLOR_SUBTITLE2,
                    ha="center", va="center", zorder=2)
        else:
            ax.text(cx, genre_y, GENRE_LINE, fontsize=genre_fontsize, fontname=str(sans_path),
                    color=COLOR_SUBTITLE2, ha="center", va="center", zorder=2)

    for ext in ["png", "pdf"]:
        out = script_dir / f"cover_front_zh.{ext}"
        fig.savefig(out, dpi=DPI, bbox_inches=None, pad_inches=0)
        print(f"Saved: {out}")

    plt.close(fig)


if __name__ == "__main__":
    generate_cover()


# sassy

