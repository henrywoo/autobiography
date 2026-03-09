# 《云层之上无风雨》

自传体小说（约 95% 真实）。从农村到小镇、大学、留学、回国、再出国；主题积极，类似《阿甘正传》的成长与时代见证。

## 主题

一人一时代：从山野到云端，在洪流中活成自己的见证。命运不是被规划的路径，而是在时代里不断打开的疆域。



---

## 全书结构（12 章 + 序章）

| 序/章 | 标题 | 内容概要 |
|-------|------|----------|
| 序章 | 我 | 断奶时第一次意识到「我」；两岁，第一次见雪 |
| 第一章 | 山 | 山村童年，泉水、螃蟹、石灰岩、泥墙雕塑 |
| 第二章 | 路 | 小学到初中，与天才同学争第一；放学走土路回家时想：为什么赢不了 |
| 第三章 | 门 | 中考、内招，以落榜生名义实为全校第二；学校满员需另交千元，家贫。父亲同学之夫负责修简阳中学校门，从修门经费中拨一千以奖学金名义予我，才得入学。门：鲤鱼跃龙门，进简阳中学即半脚跨进大学，寒门学子跃农门之望 |
| 第四章 | 火 | 高中状元、火锅店、多年后老板成首富 |
| 第五章 | 歌 | 大学美术社、书法、合唱团、美声 |
| 第六章 | 旗 | 1999 国庆游行、天安门、彭丽媛、江主席 |
| 第七章 | 海 | 出国、新加坡、托福 GRE、PhD 未读；MIT / SMA，世界级科学 |
| 第八章 | 网 | 毕业回国后，写文章被丁磊看到、被丁磊招进网易、「云层之上无风雨」 |
| 第九章 | 街 | 离开丁磊，进入华尔街对冲基金；新加坡交易所有交易执照的交易员 |
| 第十章 | 谷 | 来到 优步，当时宇宙第一的 startup，参与无人车制造 |
| 第十一章 | 云 | 加入 OCI，在云上做 AI |
| 第十二章 | 无 | 无码（编程从参加工作到 AI 时代，不再需要人写代码）；无风雨（回应云层之上无风雨）；无常（母亲生病，生命无常）；青春不在、时间流逝，一切终将归于虚无，反思生命的意义 |

素材与详细提纲见 `raw/1.txt`。

---

## 目录结构（适配 bubble 建书）

```
├── raw/
│   └── 1.txt                 # 素材与 12 章提纲
├── chapterx/
│   └── preface.md            # 序章 我
├── chapter1-shan/ … chapter12-wu/
│   └── chapterN.md           # 第 N 章
├── templates -> ../math4ai/shared/bubble/templates   # 可选，用于本地构建
├── scripts -> ../math4ai/shared/bubble/scripts        # 可选，用于本地构建
├── peanut.config             # 书名等配置
├── readme.md
└── book.pdf                  # 生成的书（见下方构建说明）
```

---

## 如何生成 PDF（bubble）

使用 [bubble](https://github.com/your-org/bubble)（路径：`/home/wukong/math4ai/shared/bubble`）从 Markdown 章节生成整书 PDF。

1. **中文字体**（模板使用 Noto Serif CJK SC）  
   - Ubuntu/Debian: `sudo apt install fonts-noto-cjk`  
   - 安装后: `fc-cache -fv`

2. **在项目根目录用 `--lang cn` 构建**  
   ```bash
   cd /home/wukong/autobiography
   PYTHONPATH=/home/wukong/math4ai/shared/bubble python /home/wukong/math4ai/shared/bubble/build_book.py --lang cn --max-chapters 12
   ```
   若本仓库已创建 `templates`、`scripts` 指向 `math4ai/shared/bubble` 的符号链接，可省略 `PYTHONPATH`。若已安装 bubble 包：
   ```bash
   bubble-build --lang cn --max-chapters 12
   ```

未加 `--lang cn` 时默认英文引擎，中文可能不显示。`--max-chapters 12` 可省略（bubble 会按当前 chapter 目录自动检测）。
