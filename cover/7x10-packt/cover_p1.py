import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
from matplotlib.patches import Circle
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image, ImageFilter

# Set random seed for reproducibility
np.random.seed(1142)

# 1. 创建画布（保留你的尺寸设置）
fig_width, fig_height = 20, 20
fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor='black')

# 关键修复：提前设置等比例缩放（确保节点圆形）
ax.set_aspect('equal', adjustable='box')  # 核心：x/y轴等比例
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# 2. 网络参数（保留你的所有设置）
n_nodes = 784
min_connections = 8

# 基础色板
base_colors = [
    '#00ccff', '#ff3366', '#33ff99', '#ffcc00', '#cc66ff',
    '#ff9966', '#66ffff', '#ff66cc', '#99ff33', '#ff3333',
]

# 辅助函数：调整颜色亮度
def adjust_color_brightness(hex_color, brightness_factor):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = int(np.clip(r * brightness_factor, 0, 255))
    g = int(np.clip(g * brightness_factor, 0, 255))
    b = int(np.clip(b * brightness_factor, 0, 255))
    return f'#{r:02x}{g:02x}{b:02x}'

# 为每个节点生成渐变配色（中心亮 → 边缘暗）
node_gradient_dict = {}
for i in range(n_nodes):
    base_color = np.random.choice(base_colors)
    # 渐变的两个端点色：中心更亮，边缘更暗
    center_color = adjust_color_brightness(base_color, 1.4)  # 中心亮色
    edge_color = adjust_color_brightness(base_color, 0.7)    # 边缘暗色
    # 阴影和高光色
    shadow_color = adjust_color_brightness(base_color, 0.5)
    highlight_color = adjust_color_brightness(base_color, 1.5)
    
    node_gradient_dict[i] = {
        'center': center_color,
        'edge': edge_color,
        'shadow': shadow_color,
        'highlight': highlight_color
    }

line_color = '#0099dd'
node_size_range = (50, 60)
line_alpha = 0.6

# 3. 生成节点坐标（保留你的范围）
x_nodes = np.random.uniform(5, 95, n_nodes)
y_nodes = np.random.uniform(5, 95, n_nodes)
node_sizes = np.random.uniform(*node_size_range, n_nodes)

# 4. 绘制连接线（保留你的逻辑）
connection_count = np.zeros(n_nodes)
for i in range(n_nodes):
    distances = np.sqrt((x_nodes[i] - x_nodes)**2 + (y_nodes[i] - y_nodes)**2)
    closest_nodes = np.argsort(distances)[1:min_connections+2]
    for j in closest_nodes:
        if i != j and connection_count[i] < min_connections:
            ax.plot(
                [x_nodes[i], x_nodes[j]], [y_nodes[i], y_nodes[j]],
                color=line_color, linewidth=1.0, alpha=line_alpha,
                zorder=1  # 线在节点下方
            )
            connection_count[i] += 1
            connection_count[j] += 1

# 5. 绘制渐变3D节点（优化圆形显示）
for i in range(n_nodes):
    x = x_nodes[i]
    y = y_nodes[i]
    size = node_sizes[i]
    # 保留你的半径换算逻辑，新增transform确保圆形
    radius = np.sqrt(size / np.pi) / 10  # 你的原始设置
    
    colors = node_gradient_dict[i]
    
    # --------------------------
    # 步骤1：阴影层（3D基础，优化圆形）
    # --------------------------
    shadow_radius = radius * 1.01
    shadow_circle = Circle(
        (x + 0.0815, y - 0.0815),  # 你的原始偏移
        shadow_radius,
        color=colors['shadow'],
        alpha=0.4,
        zorder=2,
        transform=ax.transData  # 关键：使用轴数据坐标系，确保圆形
    )
    ax.add_patch(shadow_circle)
    
    # --------------------------
    # 步骤2：渐变主体层（核心，确保圆形渐变）
    # --------------------------
    # 为当前节点创建专属的径向渐变colormap
    cmap = LinearSegmentedColormap.from_list(
        f'node_{i}', 
        [colors['center'], colors['edge']],
        N=100  # 渐变平滑度
    )
    
    # 生成严格圆形的坐标网格
    theta = np.linspace(0, 2 * np.pi, 100)  # 完整360度圆
    r = np.linspace(0, radius, 50)          # 径向距离
    THETA, R = np.meshgrid(theta, r)
    X = x + R * np.cos(THETA)
    Y = y + R * np.sin(THETA)
    
    # 用距离中心的远近作为渐变依据
    dist_from_center = R / radius
    # 绘制渐变填充的圆（优化渲染）
    ax.pcolormesh(
        X, Y, dist_from_center,
        cmap=cmap,
        alpha=0.95,
        shading='gouraud',  # 平滑渐变
        zorder=3,
        rasterized=True     # 防止矢量缩放导致的变形
    )

# 6. 保存原始图（移除无效参数，保留你的设置）
plt.savefig(
    'multi_colored_network.png',
    dpi=300,
    facecolor='white',
    bbox_inches='tight',
    pad_inches=0
)
plt.close()

# --------------------------
# 后处理：周边模糊（保留你的逻辑）
# --------------------------
def blur_image_periphery(original_path, output_path, blur_radius=35, fade_radius_ratio=0.001):
    img = Image.open(original_path).convert("RGBA")
    blurred_img = img.filter(ImageFilter.GaussianBlur(blur_radius))
    
    width, height = img.size
    center_x, center_y = width // 2, height // 2
    max_dist = np.sqrt(center_x**2 + center_y**2)
    fade_dist = max_dist * fade_radius_ratio
    
    y, x = np.ogrid[:height, :width]
    dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
    
    mask = np.clip((dist_from_center - fade_dist) / (max_dist - fade_dist), 0, 1) * 255
    mask = mask.astype(np.uint8)
    mask_img = Image.fromarray(mask, mode='L')
    
    final_img = Image.composite(blurred_img, img, mask_img)
    final_img.convert("RGB").save(output_path, dpi=(300, 300))
    print(f"渐变3D节点图已保存：{output_path}")

# 执行后处理（保留你的参数）
blur_image_periphery(
    original_path="multi_colored_network.png",
    output_path="final_gradient_3d_nodes.png",
    blur_radius=165,
    fade_radius_ratio=0.0001
)