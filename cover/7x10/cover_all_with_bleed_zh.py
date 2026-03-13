#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文书封：带 KDP 出血的环衬 PDF
- 封面：cover_front_zh.pdf
- 书脊：程序生成（中文书名、作者）
- 封底：cover_back_zh.pdf

KDP 要求：四边出血 0.125 inch，画布为 (宽+0.25) x (高+0.25) inch。

输出：cover_all_with_bleed_zh.pdf
"""

import sys
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PyPDF2 import PdfReader
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
import numpy as np

BLEED_INCHES = 0.125
BLEED_POINTS = BLEED_INCHES * 72

# 书脊文案（与封面一致）
SPINE_TITLE = "云层之上"
SPINE_AUTHOR = "玄心"


def _get_cjk_fontpaths():
    """返回 (serif_path, sans_path)，与 cover_front_zh / cover_back_zh 一致。"""
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


def get_pdf_dimensions(pdf_path):
    """获取 PDF 页面的尺寸（点）。"""
    reader = PdfReader(str(pdf_path))
    page = reader.pages[0]
    mediabox = page.mediabox
    width = float(mediabox.width)
    height = float(mediabox.height)
    return width, height


def create_spine_pdf_with_bleed(spine_width_points, height_points, output_path, serif_path, sans_path):
    """生成书脊 PDF（无出血，尺寸=内容尺寸，避免合并时被拉伸）。"""
    spine_width_inches = spine_width_points / 72.0
    height_inches = height_points / 72.0
    width = spine_width_inches
    height = height_inches

    # 书脊按内容尺寸出图，合并时 1:1 绘制，字体和圆点不会变形
    dpi = 300
    fig = plt.figure(figsize=(width, height), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)

    # 书脊背景：深蓝到浅蓝的竖向渐变（下深上浅），用 imshow 避免条纹
    dark_r, dark_g, dark_b = 0.12, 0.28, 0.58   # 深蓝
    light_r, light_g, light_b = 0.55, 0.72, 0.95  # 浅蓝
    nrows = 400
    ncols = 32
    t = np.linspace(0, 1, nrows).reshape(-1, 1)  # 0=底(深蓝), 1=顶(浅蓝)
    r = (1 - t) * dark_r + t * light_r
    g = (1 - t) * dark_g + t * light_g
    b = (1 - t) * dark_b + t * light_b
    grad = np.hstack([r, g, b]).reshape(nrows, 1, 3)
    grad = np.tile(grad, (1, ncols, 1))
    x0, x1 = -0.5, width + 0.5
    y0, y1 = 0, height  # 深蓝在顶(y=height)，浅蓝在底(y=0)
    ax.imshow(grad, extent=[x0, x1, y0, y1], aspect="auto", origin="upper", zorder=0)

    # 字号按书脊高度算，避免薄书脊时字过小；设下限保证可读
    height_pt = height * 72
    title_font_size = max(20, int(height_pt * 0.024))
    author_font_size = max(14, int(height_pt * 0.018))

    # 竖排：每字正立、自上而下，中间白点分隔（与参考图一致）
    spine_text_color = "white"
    cx = width / 2
    step_in = (title_font_size * 1.15 / 72.0)  # 字与字竖向间距
    title_top_y = height / 2 + 0.5 * step_in * 20  # 书名块顶部

    # 书名「云层之上」逐字竖排（不旋转，每字正立）
    use_serif = serif_path and Path(serif_path).exists()
    for i, ch in enumerate(SPINE_TITLE):
        y_i = title_top_y - i * step_in
        if use_serif:
            prop = fm.FontProperties(fname=serif_path)
            prop.set_size(title_font_size)
            prop.set_weight("bold")
            ax.text(cx, y_i, ch, fontproperties=prop, ha="center", va="center",
                    color=spine_text_color, zorder=21)
        else:
            ax.text(cx, y_i, ch, fontsize=title_font_size, fontname="DejaVu Serif", weight="bold",
                    color=spine_text_color, ha="center", va="center", zorder=21)

    # 白点分隔
    dot_y = title_top_y - 4 * step_in - 0.04
    dot_r = 0.05
    dot = patches.Circle((cx, dot_y), dot_r, facecolor=spine_text_color, edgecolor="none", zorder=21)
    ax.add_patch(dot)

    # 作者「玄心」竖排，下加略小略右的「著」
    author_top_y = dot_y - 0.30 - 2 * dot_r
    author_step = author_font_size * 1.1 / 72.0
    use_sans = sans_path and Path(sans_path).exists()
    for i, ch in enumerate(SPINE_AUTHOR):
        y_i = author_top_y - i * author_step
        if use_sans:
            prop = fm.FontProperties(fname=sans_path)
            prop.set_size(author_font_size)
            prop.set_weight("bold")
            ax.text(cx, y_i, ch, fontproperties=prop, ha="center", va="center",
                    color=spine_text_color, zorder=21)
        else:
            ax.text(cx, y_i, ch, fontsize=author_font_size, fontname="DejaVu Sans", weight="bold",
                    color=spine_text_color, ha="center", va="center", zorder=21)
    zhu_y = author_top_y - len(SPINE_AUTHOR) * author_step - 0.5 * author_step  # 与「玄心」留一点间距
    if use_sans:
        prop_zhu = fm.FontProperties(fname=sans_path)
        prop_zhu.set_size(author_font_size)
        prop_zhu.set_weight("bold")
        ax.text(cx + 0.02, zhu_y, "著", fontproperties=prop_zhu, ha="center", va="center",
                color=spine_text_color, zorder=21)
    else:
        ax.text(cx + 0.02, zhu_y, "著", fontsize=author_font_size, fontname="DejaVu Sans", weight="bold",
                color=spine_text_color, ha="center", va="center", zorder=21)

    # 固定画布尺寸保存，避免合并时被拉伸变形（不用 bbox_inches='tight'）
    plt.savefig(str(output_path), dpi=dpi, format="pdf",
                facecolor="white", edgecolor="none",
                bbox_inches=None, pad_inches=0)
    plt.close()


def merge_covers_with_bleed(front_pdf, spine_pdf, back_pdf, output_pdf, spine_content_width_points):
    """合并封面 + 书脊 + 封底，带 KDP 出血。"""
    import tempfile
    import shutil

    front_width, front_height = get_pdf_dimensions(front_pdf)
    back_width, back_height = get_pdf_dimensions(back_pdf)
    spine_content_width = spine_content_width_points

    content_width = front_width + spine_content_width + back_width
    content_height = front_height

    final_width_inches = (content_width / 72.0) + 2 * BLEED_INCHES
    final_height_inches = (content_height / 72.0) + 2 * BLEED_INCHES

    print(f"   内容尺寸: {content_width/72:.2f}\" x {content_height/72:.2f}\"")
    print(f"   含出血画布: {final_width_inches:.2f}\" x {final_height_inches:.2f}\"")

    c = canvas.Canvas(str(output_pdf), pagesize=(final_width_inches * inch, final_height_inches * inch))
    temp_dir = Path(tempfile.mkdtemp())

    try:
        try:
            import subprocess
            subprocess.run(["pdftoppm", "-png", "-r", "300", "-singlefile",
                           str(front_pdf), str(temp_dir / "front")], check=True, capture_output=True)
            subprocess.run(["pdftoppm", "-png", "-r", "300", "-singlefile",
                           str(spine_pdf), str(temp_dir / "spine")], check=True, capture_output=True)
            subprocess.run(["pdftoppm", "-png", "-r", "300", "-singlefile",
                           str(back_pdf), str(temp_dir / "back")], check=True, capture_output=True)

            front_img = temp_dir / "front.png"
            spine_img = temp_dir / "spine.png"
            back_img = temp_dir / "back.png"

            if front_img.exists() and spine_img.exists() and back_img.exists():
                x_offset = BLEED_INCHES * inch
                y_offset = BLEED_INCHES * inch
                c.drawImage(str(back_img), x_offset, y_offset, width=back_width, height=back_height)
                c.drawImage(str(spine_img), x_offset + back_width, y_offset,
                           width=spine_content_width, height=back_height)
                c.drawImage(str(front_img), x_offset + back_width + spine_content_width, y_offset,
                           width=front_width, height=back_height)
                c.save()
                shutil.rmtree(temp_dir)
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        try:
            from pdf2image import convert_from_path
            front_img = convert_from_path(str(front_pdf), dpi=300)[0]
            front_img.save(temp_dir / "front.png", "PNG")
            spine_img = convert_from_path(str(spine_pdf), dpi=300)[0]
            spine_img.save(temp_dir / "spine.png", "PNG")
            back_img = convert_from_path(str(back_pdf), dpi=300)[0]
            back_img.save(temp_dir / "back.png", "PNG")

            x_offset = BLEED_INCHES * inch
            y_offset = BLEED_INCHES * inch
            c.drawImage(str(temp_dir / "back.png"), x_offset, y_offset,
                        width=back_width, height=back_height, preserveAspectRatio=True)
            c.drawImage(str(temp_dir / "spine.png"), x_offset + back_width, y_offset,
                        width=spine_content_width, height=back_height, preserveAspectRatio=False)
            c.drawImage(str(temp_dir / "front.png"), x_offset + back_width + spine_content_width, y_offset,
                        width=front_width, height=back_height, preserveAspectRatio=True)
            c.save()
            shutil.rmtree(temp_dir)
            return True
        except ImportError:
            print("  需要 pdftoppm (poppler-utils) 或 pdf2image")
            print("    sudo apt-get install poppler-utils  或  pip install pdf2image pillow")
            shutil.rmtree(temp_dir)
            return False
    except Exception as e:
        print(f"  错误: {e}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return False


def calculate_spine_width(pages):
    """按页数计算书脊宽度（英寸）。薄书到厚书均支持。"""
    page_widths = {
        80: 0.35,
        100: 0.42,
        110: 0.46,
        120: 0.50,
        150: 0.58,
        200: 0.72,
        250: 0.88,
        300: 1.02,
        400: 1.18,
        500: 1.25,
        520: 1.30,
        550: 1.39,
        580: 1.45,
        600: 1.50,
    }
    if pages in page_widths:
        return page_widths[pages]
    sorted_pages = sorted(page_widths.keys())
    if pages < sorted_pages[0]:
        return page_widths[sorted_pages[0]]
    if pages > sorted_pages[-1]:
        return page_widths[sorted_pages[-1]]
    for i in range(len(sorted_pages) - 1):
        if sorted_pages[i] <= pages <= sorted_pages[i + 1]:
            p1, p2 = sorted_pages[i], sorted_pages[i + 1]
            w1, w2 = page_widths[p1], page_widths[p2]
            ratio = (pages - p1) / (p2 - p1)
            return round(w1 + ratio * (w2 - w1), 2)
    return 0.20


def main(pages=110):
    """生成中文环衬 PDF（带出血）。"""
    script_dir = Path(__file__).parent

    front_pdf = script_dir / "cover_front_zh.pdf"
    back_pdf = script_dir / "cover_back_zh.pdf"
    output_pdf = script_dir / "cover_all_with_bleed_zh.pdf"

    if not front_pdf.exists():
        print(f"❌ 未找到: {front_pdf}")
        print("   请先运行: python cover_front_zh.py")
        sys.exit(1)
    if not back_pdf.exists():
        print(f"❌ 未找到: {back_pdf}")
        print("   请先运行: python cover_back_zh.py")
        sys.exit(1)

    serif_path, sans_path = _get_cjk_fontpaths()

    print("📚 生成中文环衬（含 KDP 出血）...")
    print(f"   封面: {front_pdf}")
    print(f"   封底: {back_pdf}")
    print(f"   出血: {BLEED_INCHES:.3f}\" 四边")

    front_width, front_height = get_pdf_dimensions(front_pdf)
    back_width, back_height = get_pdf_dimensions(back_pdf)

    if abs(front_height - back_height) > 1:
        print(f"⚠️  封面/封底高度不一致，以封面为准")
    height = front_height

    spine_width_inches = calculate_spine_width(pages)
    spine_width_points = spine_width_inches * 72

    print(f"   页数: {pages}")
    print(f"   书脊宽: {spine_width_inches:.2f} inch")

    print("   生成书脊（含出血）...")
    temp_spine = script_dir / "cover_spine_zh_temp_bleed.pdf"
    create_spine_pdf_with_bleed(spine_width_points, height, temp_spine, serif_path, sans_path)

    print("   合并 封面 + 书脊 + 封底...")
    success = merge_covers_with_bleed(front_pdf, temp_spine, back_pdf, output_pdf, spine_width_points)

    if temp_spine.exists():
        temp_spine.unlink()

    if success and output_pdf.exists():
        total_width, total_height = get_pdf_dimensions(output_pdf)
        total_width_inches = total_width / 72.0
        total_height_inches = total_height / 72.0
        content_width = (front_width + spine_width_points + back_width) / 72.0
        content_height = front_height / 72.0
        print(f"\n✅ 已生成: {output_pdf}")
        print(f"   画布: {total_width_inches:.2f}\" x {total_height_inches:.2f}\"")
        print(f"   内容区: {content_width:.2f}\" x {content_height:.2f}\"")
        print(f"   布局: 封底 ({back_width/72:.2f}\") + 书脊 ({spine_width_inches:.2f}\") + 封面 ({front_width/72:.2f}\")")
        print(f"   ✅ 符合 KDP 四边 {BLEED_INCHES:.3f}\" 出血")
    else:
        print(f"\n❌ 生成失败: {output_pdf}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            pages = int(sys.argv[1])
        except ValueError:
            print(f"⚠️  页数无效，使用默认 110")
            pages = 110
    else:
        pages = 110
    main(pages)
