#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文封底：版式参照 cover_back.py（书名 / 副标题 / 简介框 / 核心看点+读者框），
两个圆角白框叠在 cover_back_bkg.png 上。CJK 用 fname 防乱码。
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.font_manager as fm
import matplotlib.patches as patches

WIDTH_IN, HEIGHT_IN = 7.0, 10.0
DPI = 300
# 与 cover_back.py 一致：scale_y = height/10，版面比例一致
scale_y = HEIGHT_IN / 10.0

# 封底文案（可改）
TITLE = "云层之上"
SUBTITLE = "从大山泉水到硅谷 AI 的生命行路"
DESC_TEXT = (
    "本书从四川深山的泉水边出发，历经北京大学生合唱团、新加坡与 MIT 的求学，"
    "到华尔街与硅谷——网易、优步、谷歌、甲骨文。\n"
    "十二个意象（山、路、门、火、歌、旗、海、网、街、谷、云、无）串联三十年；"
    "在算法与代码之外，追问生命的意义。"
)
FEATURES_HEADER = "核心看点"
FEATURES_CONTENT = (
    "• 从山村到硅谷的跨度，中国第一代互联网人的成长与选择\n"
    "• 与丁磊、张勇、Gilbert Strang 等人物互动的真实细节\n"
    "• 用诗意与哲思解读技术，探讨 ChatGPT 时代下人的价值\n"
    "• 寒门升学、异国求职与亲情觉醒的共鸣"
)
AUDIENCE_HEADER = "适合读者"
AUDIENCE_CONTENT = (
    "对个人成长、技术人文与自传体随笔感兴趣的读者；"
    "互联网与 AI 行业从业者；关注教育与阶层流动的读者。"
)
AUTHOR = "玄心  著"

COLOR_TITLE = "#222222"
COLOR_SUBTITLE = "#555555"
COLOR_BODY = "#333333"
COLOR_AUTHOR = "#444444"


def _get_cjk_fontpaths():
    """与 cover_front_zh 相同：返回 (serif_path, sans_path)。"""
    serif_path = None
    sans_path = None
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


def _text(ax, x, y, s, font_path_or_name, fontsize, color, weight="normal", ha="center", **kwargs):
    """单行/多行文字，优先 fontproperties=fname 防乱码。"""
    if isinstance(font_path_or_name, (str, Path)) and Path(font_path_or_name).exists():
        prop = fm.FontProperties(fname=str(font_path_or_name))
        prop.set_size(fontsize)
        prop.set_weight(weight)
        ax.text(x, y, s, fontproperties=prop, color=color, ha=ha, va="center", **kwargs)
    else:
        ax.text(x, y, s, fontsize=fontsize, fontname=str(font_path_or_name), weight=weight, color=color,
                ha=ha, va="center", **kwargs)


def generate_cover():
    script_dir = Path(__file__).resolve().parent
    bkg_path = script_dir / "cover_back_bkg.png"
    if not bkg_path.exists():
        raise FileNotFoundError(f"Background image not found: {bkg_path}")

    serif_path, sans_path = _get_cjk_fontpaths()
    if not serif_path:
        serif_path = "DejaVu Serif"
    if not sans_path:
        sans_path = "DejaVu Sans"

    width, height = WIDTH_IN, HEIGHT_IN
    fig = plt.figure(figsize=(width, height), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)

    img = mpimg.imread(str(bkg_path))
    ax.imshow(img, extent=[0, width, 0, height], aspect="auto", zorder=0, alpha=0.5)

    cx = width / 2.0
    body_fontsize = int(9 * scale_y)
    line_height = body_fontsize * 1.4 / 72.0
    # 与 cover_back.py 一致：正文区宽度 70%，居中
    text_width = width * 0.70
    text_x_left = (width - text_width) / 2.0
    use_prop = isinstance(sans_path, (str, Path)) and Path(sans_path).exists()

    def _body_text(x, y, s, zorder=21, **kwargs):
        if use_prop:
            prop = fm.FontProperties(fname=str(sans_path))
            prop.set_size(body_fontsize)
            ax.text(x, y, s, fontproperties=prop, color=COLOR_BODY, ha="left", va="top", zorder=zorder, **kwargs)
        else:
            ax.text(x, y, s, fontsize=body_fontsize, fontname=str(sans_path), color=COLOR_BODY,
                    ha="left", va="top", zorder=zorder, **kwargs)

    # 1) 书名（与 cover_back 同：title_y = 0.82*height）
    title_y = 0.82 * height
    _text(ax, cx, title_y, TITLE, serif_path, int(14 * scale_y), COLOR_TITLE, weight="bold", zorder=21)
    # 2) 副标题（subtitle_y = 0.78*height）
    subtitle_y = 0.78 * height
    _text(ax, cx, subtitle_y, SUBTITLE, sans_path, int(12 * scale_y), COLOR_SUBTITLE, zorder=21)

    # 与 cover_back.py 一致：两个圆角白框
    box_padding = 0.165
    box_width = width * 0.70
    box_x = (width - box_width) / 2
    corner_radius = 0.15

    # 3) 简介框（略高一点）
    desc_lines = DESC_TEXT.count("\n") + 1
    desc_box_height = (desc_lines * body_fontsize * 1.4 / 72 + box_padding * 2) * 1.4
    desc_box_y = 0.75 * height - desc_box_height
    desc_box = patches.FancyBboxPatch(
        (box_x, desc_box_y), box_width, desc_box_height,
        boxstyle=f"round,pad=0.02,rounding_size={corner_radius}",
        linewidth=1, edgecolor="grey", facecolor="white", alpha=0.7, zorder=20
    )
    ax.add_patch(desc_box)
    desc_text_x = box_x + box_padding
    desc_text_y = desc_box_y + desc_box_height - box_padding
    _body_text(desc_text_x, desc_text_y, DESC_TEXT, linespacing=1.4)

    # 4) 核心看点 + 适合读者 合并框
    combined_lines = (
        FEATURES_CONTENT.count("\n") + 1 + AUDIENCE_CONTENT.count("\n") + 1 + 6
    )
    combined_box_height = combined_lines * body_fontsize * 1.4 / 72 + box_padding * 2
    combined_box_y = 0.50 * height - combined_box_height
    combined_box = patches.FancyBboxPatch(
        (box_x, combined_box_y), box_width, combined_box_height,
        boxstyle=f"round,pad=0.02,rounding_size={corner_radius}",
        linewidth=1, edgecolor="grey", facecolor="white", alpha=0.7, zorder=20
    )
    ax.add_patch(combined_box)

    combined_text_x = box_x + box_padding
    y_pos = combined_box_y + combined_box_height - box_padding

    if use_prop:
        prop_bold = fm.FontProperties(fname=str(sans_path))
        prop_bold.set_size(body_fontsize)
        prop_bold.set_weight("bold")
    # 核心看点 标题
    if use_prop:
        ax.text(combined_text_x, y_pos, FEATURES_HEADER, fontproperties=prop_bold, color=COLOR_BODY, ha="left", va="top", zorder=21)
    else:
        ax.text(combined_text_x, y_pos, FEATURES_HEADER, fontsize=body_fontsize, fontname=str(sans_path), weight="bold", color=COLOR_BODY, ha="left", va="top", zorder=21)
    y_pos -= line_height * 2
    _body_text(combined_text_x, y_pos, FEATURES_CONTENT, linespacing=1.4)
    y_pos -= (FEATURES_CONTENT.count("\n") + 1) * line_height + line_height * 2
    # 适合读者 标题
    if use_prop:
        ax.text(combined_text_x, y_pos, AUDIENCE_HEADER, fontproperties=prop_bold, color=COLOR_BODY, ha="left", va="top", zorder=21)
    else:
        ax.text(combined_text_x, y_pos, AUDIENCE_HEADER, fontsize=body_fontsize, fontname=str(sans_path), weight="bold", color=COLOR_BODY, ha="left", va="top", zorder=21)
    y_pos -= line_height * 2
    _body_text(combined_text_x, y_pos, AUDIENCE_CONTENT, linespacing=1.4)

    # 5) 作者（靠下）
    author_y = 0.55
    _text(ax, cx, author_y, AUTHOR, sans_path, int(10 * scale_y), COLOR_AUTHOR, zorder=21)

    for ext in ["png", "pdf"]:
        out = script_dir / f"cover_back_zh.{ext}"
        fig.savefig(out, dpi=DPI, bbox_inches=None, pad_inches=0)
        print(f"Saved: {out}")
    plt.close(fig)


if __name__ == "__main__":
    generate_cover()
