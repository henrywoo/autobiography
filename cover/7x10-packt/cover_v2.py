import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import numpy as np

# Create figure and axis
fig = plt.figure(figsize=(9, 12), facecolor='#1a1a1a')
ax = fig.add_axes([0, 0, 1, 1], facecolor='#1a1a1a')
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# --- 1. Top network banner ---
# Draw network nodes and lines (simplified)
np.random.seed(42)
n_nodes = 25
x_nodes = np.random.uniform(5, 95, n_nodes)
y_nodes = np.random.uniform(70, 95, n_nodes)

# Draw edges
for i in range(n_nodes):
    for j in range(i+1, n_nodes):
        if np.random.random() < 0.15:  # Random edge density
            ax.plot([x_nodes[i], x_nodes[j]], [y_nodes[i], y_nodes[j]],
                    color='#00a8ff', linewidth=1.2, alpha=0.7)

# Draw nodes
ax.scatter(x_nodes, y_nodes, color='#00a8ff', s=60, alpha=0.9)

# --- 2. Packt logo ---
ax.text(85, 97, '<packt>', color='#ff6633', fontsize=22,
        fontweight='bold', ha='right', va='top')

# --- 3. Edition label ---
edition_rect = Rectangle((78, 62), 18, 4, color='#ff6633')
ax.add_patch(edition_rect)
ax.text(87, 64, '1ST EDITION', color='white', fontsize=10,
        fontweight='bold', ha='center', va='center')

# --- 4. Main title ---
ax.text(50, 45, 'Distributed AI Systems', color='white', fontsize=32,
        fontweight='bold', ha='center', va='center')

# --- 5. Subtitle ---
subtitle = "A practical guide to building scalable training,\ninference, and serving systems for production AI"
ax.text(50, 32, subtitle, color='white', fontsize=14,
        ha='center', va='center', linespacing=1.5)

# --- 6. Author name ---
ax.text(85, 10, 'FUHENG WU', color='white', fontsize=18,
        fontweight='bold', ha='right', va='bottom')

# --- 7. Corner accent (orange lines) ---
ax.plot([5, 10], [10, 5], color='#ff6633', linewidth=3)
ax.plot([8, 13], [10, 5], color='#ff6633', linewidth=3)

# Save/show the result
plt.savefig('distributed_ai_systems_cover.png', dpi=300, facecolor='#1a1a1a')
plt.show()
