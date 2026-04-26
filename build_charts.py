"""Generate chart PNGs + product mock screenshots for the investor deck."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

ASSETS = Path(__file__).parent / "deck_assets"
ASSETS.mkdir(exist_ok=True)

# Brand palette
NAVY = "#0B1F3A"
ACCENT = "#29B6F6"
PINK = "#FF3D7F"
GOLD = "#F7B731"
DARK = "#0E0E12"
LIGHT = "#F5F7FA"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.edgecolor": "#CCCCCC",
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def save(fig, name):
    out = ASSETS / name
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


# ---- 1. Why-now: short-form video market growth (Statista-like trend) ---
fig, ax = plt.subplots(figsize=(9, 4.5))
years = np.arange(2020, 2031)
# Approx short-form video ad spend ($B), with smooth growth curve.
spend = np.array([18, 32, 56, 88, 130, 184, 246, 314, 386, 460, 540])
ax.fill_between(years, 0, spend, color=ACCENT, alpha=0.25)
ax.plot(years, spend, color=NAVY, linewidth=3, marker="o", markersize=6)
ax.axvline(2026, color=PINK, linestyle="--", linewidth=1.2, alpha=0.7)
ax.text(2026.1, 50, "Clipsmith\nlaunch", color=PINK, fontsize=10, fontweight="bold")
ax.set_title("Short-form video ad spend ($B)", fontsize=14, fontweight="bold", color=NAVY, loc="left")
ax.set_ylabel("USD billions")
ax.set_xticks(years[::2])
ax.grid(axis="y", alpha=0.3)
ax.set_ylim(0, 600)
save(fig, "trend_market.png")

# ---- 2. TAM / SAM / SOM ----
fig, ax = plt.subplots(figsize=(9, 4.5))
labels = ["TAM\nGlobal short-video\n+ creator economy", "SAM\nEnglish-speaking\ncreator-first apps", "SOM\nYear-3 target\nshare"]
values = [300, 60, 1.5]
colors = [NAVY, ACCENT, PINK]
bars = ax.barh(labels, values, color=colors, alpha=0.9, edgecolor="white", linewidth=2)
for bar, v in zip(bars, values):
    ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
            f"${v}B" if v >= 10 else f"${v}B (~0.5%)",
            va="center", fontsize=12, fontweight="bold", color=NAVY)
ax.set_xlim(0, 360)
ax.set_xlabel("USD billions (2027 forecast)")
ax.set_title("Market opportunity", fontsize=14, fontweight="bold", color=NAVY, loc="left")
ax.invert_yaxis()
ax.grid(axis="x", alpha=0.3)
save(fig, "tam_sam_som.png")

# ---- 3. Creator economy headcount trend ----
fig, ax = plt.subplots(figsize=(9, 4.5))
years = np.arange(2018, 2031)
creators = np.array([6, 14, 28, 50, 75, 110, 150, 200, 257, 320, 390, 465, 545])  # millions
ax.bar(years, creators, color=ACCENT, alpha=0.85, edgecolor=NAVY, linewidth=0.5)
ax.set_title("Global creators monetising content (millions)", fontsize=14, fontweight="bold", color=NAVY, loc="left")
ax.set_ylabel("Millions")
ax.set_xticks(years[::2])
ax.grid(axis="y", alpha=0.3)
for x, y in zip(years, creators):
    if x in (2020, 2024, 2028):
        ax.text(x, y + 12, f"{y}M", ha="center", fontsize=10, fontweight="bold", color=NAVY)
save(fig, "creator_growth.png")

# ---- 4. Competitive positioning matrix ----
fig, ax = plt.subplots(figsize=(8, 7))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axhline(5, color="#999", linewidth=0.8)
ax.axvline(5, color="#999", linewidth=0.8)
companies = [
    # (name, x_creator_economics, y_editing_depth, color, size)
    ("TikTok",   3.0, 3.5, "#000000", 1500),
    ("Instagram\nReels", 2.5, 3.0, "#E1306C", 1200),
    ("YouTube\nShorts", 4.0, 5.0, "#FF0000", 1300),
    ("Snapchat\nSpotlight", 4.5, 3.0, "#FFFC00", 700),
    ("Triller",  5.5, 5.5, "#00C8FF", 400),
    ("CapCut\n(editor only)", 1.5, 8.5, "#5A2DD5", 600),
    ("Clipsmith", 8.5, 8.5, PINK, 1800),
]
for name, x, y, c, s in companies:
    ax.scatter(x, y, s=s, color=c, alpha=0.85, edgecolors="white", linewidths=2, zorder=2)
    ax.annotate(name, (x, y), ha="center", va="center", fontsize=8.5,
                fontweight="bold", color="white" if name not in ("Snapchat\nSpotlight",) else NAVY,
                zorder=3)
ax.set_xlabel("Creator-favourable economics →", fontsize=12, fontweight="bold", color=NAVY)
ax.set_ylabel("In-app editing depth →", fontsize=12, fontweight="bold", color=NAVY)
ax.set_title("Where Clipsmith plays", fontsize=14, fontweight="bold", color=NAVY, loc="left")
ax.text(2.5, 9.5, "Pro tools, weak monetization", color="#666", fontsize=9, style="italic")
ax.text(7, 9.5, "Pro tools + creator-first $", color=NAVY, fontsize=9, style="italic", fontweight="bold")
ax.text(2.5, 1.2, "Big audience, opaque payouts", color="#666", fontsize=9, style="italic")
ax.text(7, 1.2, "(open quadrant)", color="#666", fontsize=9, style="italic")
ax.set_xticks([])
ax.set_yticks([])
save(fig, "competitive_matrix.png")

# ---- 5. Traction roadmap (waterfall of milestones over 24 months) ----
fig, ax = plt.subplots(figsize=(11, 4.5))
months = list(range(0, 25))
mau = [0, 0.5, 2, 5, 12, 25, 45, 80, 130, 190, 270, 360, 470, 600, 760, 940, 1140, 1360, 1600, 1850, 2120, 2400, 2700, 3000, 3300]
mau = [m / 1000 for m in mau]  # to millions
ax.fill_between(months, 0, mau, color=ACCENT, alpha=0.3)
ax.plot(months, mau, color=NAVY, linewidth=3)
milestones = [
    (3, mau[3], "TestFlight"),
    (6, mau[6], "App Store launch"),
    (9, mau[9], "Creator Fund opens"),
    (12, mau[12], "1M MAU"),
    (18, mau[18], "Brand marketplace GA"),
    (24, mau[24], "3M MAU / Series A"),
]
for x, y, label in milestones:
    ax.scatter([x], [y], color=PINK, s=80, zorder=3)
    ax.annotate(label, (x, y), xytext=(0, 18), textcoords="offset points",
                ha="center", fontsize=9, fontweight="bold", color=NAVY,
                arrowprops=dict(arrowstyle="-", color=PINK, lw=1))
ax.set_title("Projected MAU & milestones (months from launch)", fontsize=14, fontweight="bold", color=NAVY, loc="left")
ax.set_xlabel("Month from launch")
ax.set_ylabel("Monthly active users (millions)")
ax.set_xticks([0, 3, 6, 9, 12, 15, 18, 21, 24])
ax.grid(axis="y", alpha=0.3)
save(fig, "traction_roadmap.png")

# ---- 6. Use of funds donut ----
fig, ax = plt.subplots(figsize=(8, 6))
buckets = ["Engineering &\nProduct", "Content &\ncreator seeding", "Marketing &\ngrowth", "Infrastructure\n& storage", "Trust & safety", "Reserve"]
shares = [38, 22, 18, 12, 7, 3]
colors = [NAVY, PINK, ACCENT, GOLD, "#7E57C2", "#999999"]
wedges, texts, autotexts = ax.pie(
    shares, labels=buckets, colors=colors,
    autopct="%1.0f%%", startangle=90, pctdistance=0.78,
    wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2),
    textprops=dict(fontsize=10, fontweight="bold"),
)
for t in autotexts:
    t.set_color("white")
    t.set_fontsize(11)
ax.text(0, 0.05, "$3.5M", ha="center", va="center", fontsize=24, fontweight="bold", color=NAVY)
ax.text(0, -0.18, "seed round", ha="center", va="center", fontsize=11, color="#666")
ax.set_title("Use of funds — 18-month runway", fontsize=14, fontweight="bold", color=NAVY, loc="left")
save(fig, "use_of_funds.png")

# ---- 7. Unit economics bar chart ----
fig, ax = plt.subplots(figsize=(9, 4.5))
metrics = ["Tip rev /\nactive viewer", "Sub rev /\nsubscriber", "Brand-deal /\ncreator", "Premium /\npaid view"]
arpu = [0.85, 4.20, 320, 1.15]
margins = [70, 70, 90, 70]  # platform take %
x = np.arange(len(metrics))
ax.bar(x - 0.2, arpu, 0.4, color=ACCENT, label="Revenue / unit (USD)", alpha=0.85)
ax2 = ax.twinx()
ax2.bar(x + 0.2, margins, 0.4, color=PINK, label="Platform take (%)", alpha=0.85)
ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=10)
ax.set_ylabel("Revenue per unit (USD)", color=ACCENT)
ax2.set_ylabel("Platform take (%)", color=PINK)
ax.set_title("Unit economics — 4 revenue streams", fontsize=14, fontweight="bold", color=NAVY, loc="left")
ax.set_ylim(0, max(arpu) * 1.3)
ax2.set_ylim(0, 100)
ax2.spines["top"].set_visible(False)
for i, v in enumerate(arpu):
    ax.text(i - 0.2, v + 5, f"${v}", ha="center", fontsize=9, fontweight="bold", color=NAVY)
for i, v in enumerate(margins):
    ax2.text(i + 0.2, v + 2, f"{v}%", ha="center", fontsize=9, fontweight="bold", color=NAVY)
save(fig, "unit_economics.png")


# ---- 8. Product mock screenshots — 3 phone frames ----
def phone_frame(content_fn, title):
    fig, ax = plt.subplots(figsize=(3, 6.5))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 200)
    ax.axis("off")

    # Phone bezel
    bezel = plt.Rectangle((2, 4), 96, 192, linewidth=2, edgecolor=NAVY,
                          facecolor=DARK, capstyle="round", joinstyle="round")
    ax.add_patch(bezel)
    # Notch
    ax.add_patch(plt.Rectangle((36, 188), 28, 6, color=NAVY, zorder=3))
    # Inner screen
    screen = plt.Rectangle((6, 10), 88, 180, color=DARK, zorder=2)
    ax.add_patch(screen)
    content_fn(ax)
    ax.text(50, 1, title, ha="center", fontsize=10, fontweight="bold", color=NAVY)
    return fig


def feed_screen(ax):
    # Background gradient feel via stacked rects
    for i, c in enumerate(["#1a1a24", "#2c1f3d", "#3a1a3a"]):
        ax.add_patch(plt.Rectangle((6, 10 + i * 60), 88, 60, color=c, zorder=3))
    # Creator avatar circle
    ax.add_patch(plt.Circle((20, 160), 6, color=PINK, zorder=4))
    ax.text(35, 162, "@traveling_pia", color="white", fontsize=8, fontweight="bold", zorder=4)
    ax.text(35, 156, "Following · 2h", color="#bbb", fontsize=6, zorder=4)
    # Caption
    ax.text(10, 60, "Sunset over\nFaroe Islands 🌅\n#travel #vlog", color="white",
            fontsize=8, fontweight="bold", zorder=4)
    # Engagement bar
    icons = ["♥ 12.4k", "💬 387", "↪ 2.1k", "$ Tip"]
    for i, ic in enumerate(icons):
        ax.text(85, 145 - i * 15, ic, color="white", fontsize=6.5, ha="right", zorder=4)
    # Progress bar
    ax.add_patch(plt.Rectangle((10, 22), 80, 1.5, color="#444", zorder=4))
    ax.add_patch(plt.Rectangle((10, 22), 30, 1.5, color=PINK, zorder=5))


def editor_screen(ax):
    ax.add_patch(plt.Rectangle((6, 10), 88, 180, color="#1a1a1a", zorder=3))
    # Preview window
    ax.add_patch(plt.Rectangle((10, 130), 80, 50, color="#222", edgecolor="#444", linewidth=0.5, zorder=4))
    ax.text(50, 155, "▶", fontsize=24, color=PINK, ha="center", zorder=5)
    # Multi-track timeline
    track_colors = [ACCENT, GOLD, "#7E57C2", "#26A69A"]
    track_labels = ["Video", "Captions", "Music", "FX"]
    for i, (c, label) in enumerate(zip(track_colors, track_labels)):
        y = 100 - i * 14
        ax.text(8, y + 4, label, color="#bbb", fontsize=5)
        # Empty track bg
        ax.add_patch(plt.Rectangle((22, y), 65, 10, color="#2a2a2a", zorder=4))
        # Clips on track
        for cx, cw in [(22, 30), (54, 20), (76, 11)] if i == 0 else [(22, 50)] if i == 1 else [(28, 40)] if i == 2 else [(40, 18)]:
            ax.add_patch(plt.Rectangle((cx, y + 1), cw, 8, color=c, alpha=0.85, zorder=5))
    # Bottom toolbar
    for i, ic in enumerate(["✂", "+", "🎨", "🎵", "✨"]):
        ax.text(15 + i * 16, 22, ic, color="white", fontsize=10, ha="center", zorder=4)


def creator_screen(ax):
    ax.add_patch(plt.Rectangle((6, 10), 88, 180, color="white", zorder=3))
    # Header
    ax.text(50, 178, "Creator dashboard", color=NAVY, fontsize=8, fontweight="bold", ha="center", zorder=4)
    # 3 KPI cards
    kpis = [("Earnings", "$4,287", PINK), ("MAU", "182k", ACCENT), ("Subs", "1,420", GOLD)]
    for i, (label, val, c) in enumerate(kpis):
        x = 12 + i * 27
        ax.add_patch(plt.Rectangle((x, 145), 24, 22, color=c, alpha=0.15, zorder=4))
        ax.text(x + 12, 158, val, color=c, fontsize=8, fontweight="bold", ha="center", zorder=5)
        ax.text(x + 12, 150, label, color=NAVY, fontsize=5.5, ha="center", zorder=5)
    # Chart area
    ax.add_patch(plt.Rectangle((12, 70), 76, 65, color="#f5f5f7", zorder=4))
    ax.text(50, 130, "Earnings · 30 days", color=NAVY, fontsize=6.5, ha="center", zorder=5)
    # Mini line chart
    xs = np.linspace(15, 85, 30)
    ys = 80 + np.cumsum(np.random.RandomState(7).randn(30) * 1.8) + np.linspace(0, 18, 30)
    ax.plot(xs, ys, color=PINK, linewidth=1.5, zorder=5)
    ax.fill_between(xs, 75, ys, color=PINK, alpha=0.18, zorder=4)
    # Posting recs row
    ax.text(12, 60, "Best post times", color=NAVY, fontsize=6.5, fontweight="bold", zorder=5)
    times = [("Wed 12", "★★★"), ("Fri 18", "★★★"), ("Sun 19", "★★")]
    for i, (t, s) in enumerate(times):
        x = 12 + i * 26
        ax.add_patch(plt.Rectangle((x, 38), 24, 16, color="#f0f0f5", zorder=4))
        ax.text(x + 12, 47, t, color=NAVY, fontsize=6, fontweight="bold", ha="center", zorder=5)
        ax.text(x + 12, 41, s, color=PINK, fontsize=6, ha="center", zorder=5)


for fn, title, name in [
    (feed_screen, "Personalised feed", "phone_feed.png"),
    (editor_screen, "Multi-track editor", "phone_editor.png"),
    (creator_screen, "Creator dashboard", "phone_dashboard.png"),
]:
    save(phone_frame(fn, title), name)


# ---- 9. Cover background — abstract gradient ----
fig, ax = plt.subplots(figsize=(13.33, 7.5))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")
# Diagonal gradient via many stripes
for i in range(120):
    alpha = (i / 120) ** 1.2
    color_rgb = (
        0.04 + 0.02 * (1 - alpha),
        0.12 + 0.08 * (1 - alpha),
        0.23 + 0.15 * (1 - alpha),
    )
    ax.add_patch(plt.Rectangle((-20 + i * 1.2, -20), 2, 140, color=color_rgb, zorder=1))
# Pink glow circles
ax.add_patch(plt.Circle((85, 85), 18, color=PINK, alpha=0.12, zorder=2))
ax.add_patch(plt.Circle((90, 80), 8, color=PINK, alpha=0.18, zorder=2))
ax.add_patch(plt.Circle((10, 15), 22, color=ACCENT, alpha=0.10, zorder=2))
fig.savefig(ASSETS / "cover_bg.png", dpi=180, bbox_inches="tight", facecolor=DARK, pad_inches=0)
plt.close(fig)
print(f"wrote {ASSETS}/cover_bg.png")
