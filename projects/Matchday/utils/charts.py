import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from pathlib import Path
import base64
import io

def file_mtime(path):
    """Get file modification time"""
    p = Path(path)
    if not p.exists():
        return 0
    return p.stat().st_mtime

def load_master_xlsx(path, mtime):
    """Load master Excel file - cache could be added here"""
    return pd.read_excel(path, sheet_name="MASTER")

def compute_percentiles(df, metrics, group_col=None):
    """Compute percentiles for metrics"""
    out = df.copy()
    for m in metrics:
        if m not in out.columns:
            continue
        if group_col is None:
            out[m + "_pct"] = out[m].rank(pct=True) * 100
        else:
            out[m + "_pct"] = out.groupby(group_col)[m].rank(pct=True) * 100
    return out

def draw_radial(ax, labels, vals_0_1, colors, group_bounds, ax_bg="#071421", separator_color="#ffffff"):
    """Draw radial chart on matplotlib axes"""
    SEP_THIN, SEP_THICK = 1.4, 2.6
    inner_radius = 0.32
    outer_radius = inner_radius + 0.92
    inner_overlay = inner_radius + 0.05
    scale = outer_radius - inner_overlay
    theta_circle = np.linspace(0, 2 * np.pi, 720)

    vals = np.array(vals_0_1, dtype=float)
    VIS_MIN = 0.06
    vals_plot = np.where(vals > 0, np.maximum(vals, VIS_MIN), 0.0)

    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    width = 2 * np.pi / n

    ax.set_facecolor(ax_bg)
    ax.set_ylim(0, outer_radius + 0.22)

    ax.bar(angles, vals_plot * scale, width=width, bottom=inner_overlay, align="edge", color=colors, zorder=2)

    for ang in angles:
        ax.plot([ang, ang], [inner_overlay, outer_radius], linewidth=SEP_THIN, color=separator_color, zorder=3)

    for b in group_bounds:
        if b >= n:
            continue
        ang = angles[b]
        ax.plot([ang, ang], [inner_overlay, outer_radius], linewidth=SEP_THICK, color=separator_color, zorder=4)

    ax.plot(theta_circle, np.full_like(theta_circle, outer_radius), color=separator_color, linewidth=SEP_THICK, zorder=5, clip_on=False)
    ax.plot(theta_circle, np.full_like(theta_circle, inner_overlay), color=separator_color, linewidth=SEP_THICK, zorder=6, clip_on=False)

    for r in np.linspace(inner_overlay, outer_radius, 6)[1:-1]:
        ax.plot(theta_circle, np.full_like(theta_circle, r), color="white", linewidth=0.7, alpha=0.20, zorder=1)

    for ang, lab in zip(angles + width / 2, labels):
        t = ax.text(ang, outer_radius + 0.12, lab, ha="center", va="center", fontsize=9, fontweight="bold", color="white", zorder=10)
        t.set_path_effects([path_effects.Stroke(linewidth=2.0, foreground="black"), path_effects.Normal()])

    ax.set_xticks([])
    ax.set_thetagrids([])
    ax.set_yticklabels([])

def build_radial_figure(labels, vals_0_1, colors, group_bounds, ax_bg="#071421"):
    """Build complete radial figure"""
    fig = plt.figure(figsize=(7.4, 7.4), facecolor=ax_bg)
    ax = plt.subplot(111, polar=True)
    draw_radial(ax, labels, vals_0_1, colors, group_bounds, ax_bg)
    fig.patch.set_facecolor(ax_bg)
    fig.tight_layout(pad=1.0)
    return fig

def figure_to_base64(fig):
    """Convert matplotlib figure to base64 string for HTML embedding"""
    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='png', facecolor=fig.get_facecolor(), transparent=True, bbox_inches='tight')
    img_buffer.seek(0)
    img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    plt.close(fig)  # Clean up memory
    return img_data

def get_3d_model_base64(path="static/images/SoccerBall/FootBall.glb"):
    """Get base64 encoded 3D model"""
    glb_path = Path(path)
    if glb_path.exists():
        with open(glb_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""