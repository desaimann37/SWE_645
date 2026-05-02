"""
Generates a Mermaid-style LangGraph flowchart PNG using matplotlib.
All 13 nodes and every edge are included.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

OUT = "langgraph-mermaid.png"

fig, ax = plt.subplots(figsize=(13, 18))
ax.set_xlim(0, 13)
ax.set_ylim(0, 18)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# ── Colors ──────────────────────────────────────────────────────────────────
CLR = {
    "start_end": "#1e293b",
    "io":        "#dbeafe",
    "intent":    "#ede9fe",
    "create":    "#bbf7d0",
    "read":      "#bfdbfe",
    "update":    "#fed7aa",
    "delete":    "#fecaca",
    "exec":      "#a7f3d0",
    "response":  "#f1f5f9",
    "misc":      "#e2e8f0",
}

# ── Helpers ──────────────────────────────────────────────────────────────────
def box(x, y, w, h, color, label, sub="", border="#374151", lw=1.5,
        fs=9.5, sfs=8, radius=0.25):
    r = FancyBboxPatch((x - w/2, y - h/2), w, h,
                       boxstyle=f"round,pad=0.04,rounding_size={radius}",
                       linewidth=lw, edgecolor=border,
                       facecolor=color, zorder=3)
    ax.add_patch(r)
    dy = 0.16 if sub else 0
    ax.text(x, y + dy, label, ha="center", va="center",
            fontsize=fs, fontweight="bold", color="#1e293b", zorder=4,
            fontfamily="monospace")
    if sub:
        ax.text(x, y - 0.2, sub, ha="center", va="center",
                fontsize=sfs, color="#6b7280", style="italic", zorder=4)

def circle(x, y, label, color="#1e293b"):
    c = plt.Circle((x, y), 0.32, color=color, zorder=4)
    ax.add_patch(c)
    ax.text(x, y, label, ha="center", va="center",
            fontsize=10, fontweight="bold", color="white", zorder=5)

def arrow(x1, y1, x2, y2, label="", color="#6b7280", rad=0.0, lw=1.6):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                connectionstyle=f"arc3,rad={rad}"), zorder=5)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        offset = 0.22 if rad == 0 else 0.35
        ax.text(mx + offset * (1 if rad > 0 else 0),
                my + (0.18 if rad == 0 else 0),
                label, ha="center", va="center",
                fontsize=7.5, color="#374151", style="italic",
                bbox=dict(fc="white", ec="none", pad=1), zorder=6)

def side_label(x, y, label, color="#6b7280"):
    ax.text(x, y, label, ha="center", va="center",
            fontsize=7.5, color=color, style="italic", zorder=6)

# ── Title ────────────────────────────────────────────────────────────────────
ax.text(6.5, 17.55, "LangGraph Agent — Full Node & Edge Diagram",
        ha="center", fontsize=14, fontweight="bold", color="#1e293b")
ax.text(6.5, 17.2, "Student Survey Agentic AI  •  SWE 645",
        ha="center", fontsize=9, color="#6b7280")
ax.axhline(17.0, color="#e2e8f0", lw=1.5)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN SPINE  (center column x=6.5)
# Y positions (top to bottom): START 16.5, input 15.6, intent 14.5
# ─────────────────────────────────────────────────────────────────────────────
circle(6.5, 16.5, "START")
box(6.5, 15.6, 2.2, 0.65, CLR["io"], "input_node", "read user_query")
box(6.5, 14.5, 2.4, 0.72, CLR["intent"], "intent_node",
    "LLM → classify intent", border="#7c3aed", lw=2)

arrow(6.5, 16.18, 6.5, 15.93)
arrow(6.5, 15.27, 6.5, 14.87)

# Router label
ax.text(6.5, 14.0, "_route_from_intent()",
        ha="center", fontsize=8.5, fontweight="bold",
        color="#7c3aed", style="italic")

# ─────────────────────────────────────────────────────────────────────────────
# BRANCH COLUMNS
#  create=1.6  read=4.2  cancel/unknown=6.5  update=8.8  delete=11.4
# ─────────────────────────────────────────────────────────────────────────────
BX = {"create": 1.6, "read": 4.2, "cu": 6.5, "update": 8.8, "delete": 11.4}
BRANCH_TOP = 13.1

# Fan-out arrows from intent to branch tops
for key, bx in BX.items():
    arrow(6.5, 14.14, bx, BRANCH_TOP + 0.38, color="#94a3b8", lw=1.3)

# Branch intent labels
branch_labels = [
    (BX["create"],  13.65, "create",  "#15803d"),
    (BX["read"],    13.65, "read",    "#1d4ed8"),
    (BX["cu"],      13.65, "cancel/\nunknown", "#6b7280"),
    (BX["update"],  13.65, "update",  "#c2410c"),
    (BX["delete"],  13.65, "delete",  "#dc2626"),
]
for bx, by, lbl, clr in branch_labels:
    ax.text(bx, by, lbl, ha="center", fontsize=7.8,
            color=clr, fontweight="bold")

# ─── CREATE branch ─────────────────────────────────────────────────────────
cx = BX["create"]
box(cx, 12.55, 2.3, 0.72, CLR["create"], "create_extract", "extract fields (LLM)")
box(cx, 11.45, 2.4, 0.75, CLR["create"], "create_ask_or_confirm",
    "ask missing / confirm", border="#16a34a", lw=1.8)

# awaiting = create_fields
ax.text(cx - 1.55, 10.95, "missing?", fontsize=7.5, color="#6b7280", style="italic")
ax.text(cx - 1.55, 10.7, "→ awaiting=\ncreate_fields", fontsize=7, color="#15803d")

# awaiting = create_confirm
ax.text(cx + 0.9, 10.85, "all fields\ncollected?", fontsize=7.5, color="#6b7280", style="italic")
ax.text(cx + 0.9, 10.55, "→ awaiting=\ncreate_confirm", fontsize=7, color="#15803d")

box(cx, 9.85, 2.2, 0.7, CLR["exec"], "create_execute", "MCP: create_survey()",
    border="#15803d", lw=2)

arrow(cx, BRANCH_TOP, cx, 12.91)
arrow(cx, 12.19, cx, 11.83)
arrow(cx, 11.07, cx, 10.2)
# Confirmation loop arrow (yes → create_execute)
ax.annotate("", xy=(cx, 10.2), xytext=(cx + 1.3, 11.08),
            arrowprops=dict(arrowstyle="-|>", color="#15803d", lw=1.3,
                            connectionstyle="arc3,rad=-0.4"), zorder=5)
side_label(cx + 1.85, 10.6, '"yes"', "#15803d")

# ─── READ branch ──────────────────────────────────────────────────────────
cx = BX["read"]
box(cx, 12.35, 2.3, 0.75, CLR["read"], "read_execute",
    "MCP: list/search_surveys()", border="#1d4ed8", lw=1.8)
arrow(cx, BRANCH_TOP, cx, 12.73)

# ─── CANCEL / UNKNOWN branch ──────────────────────────────────────────────
cx = BX["cu"]
box(cx, 12.35, 2.2, 0.65, CLR["misc"], "cancel_node", "clear draft/target")
box(cx, 11.35, 2.2, 0.65, CLR["misc"], "unknown_node", "show help text")
arrow(cx, BRANCH_TOP, cx, 12.68)
arrow(6.5, 13.65, 6.5, 12.68, color="#94a3b8")

# ─── UPDATE branch ────────────────────────────────────────────────────────
cx = BX["update"]
box(cx, 12.55, 2.3, 0.72, CLR["update"], "update_resolve", "find target + LLM extract")
box(cx, 11.45, 2.4, 0.75, CLR["update"], "awaiting=update_confirm",
    "show proposed changes", border="#c2410c", lw=1.8)
box(cx, 9.85, 2.2, 0.7, CLR["exec"], "update_execute", "MCP: update_survey()",
    border="#15803d", lw=2)

arrow(cx, BRANCH_TOP, cx, 12.91)
arrow(cx, 12.19, cx, 11.83)
arrow(cx, 11.07, cx, 10.2)
ax.annotate("", xy=(cx, 10.2), xytext=(cx + 1.3, 11.08),
            arrowprops=dict(arrowstyle="-|>", color="#15803d", lw=1.3,
                            connectionstyle="arc3,rad=-0.4"), zorder=5)
side_label(cx + 1.85, 10.6, '"yes"', "#15803d")
side_label(cx - 1.5, 10.6, '"no" →\ncancel', "#dc2626")

# ─── DELETE branch ────────────────────────────────────────────────────────
cx = BX["delete"]
box(cx, 12.55, 2.3, 0.72, CLR["delete"], "delete_resolve",
    "find target by name/ID", border="#dc2626", lw=1.8)
box(cx, 11.45, 2.4, 0.75, CLR["delete"], "awaiting=delete_confirm",
    "show survey details", border="#dc2626", lw=2)
box(cx, 9.85, 2.2, 0.7, CLR["exec"], "delete_execute", "MCP: delete_survey()",
    border="#15803d", lw=2)

arrow(cx, BRANCH_TOP, cx, 12.91)
arrow(cx, 12.19, cx, 11.83)
arrow(cx, 11.07, cx, 10.2)
ax.annotate("", xy=(cx, 10.2), xytext=(cx + 1.3, 11.08),
            arrowprops=dict(arrowstyle="-|>", color="#15803d", lw=1.3,
                            connectionstyle="arc3,rad=-0.4"), zorder=5)
side_label(cx + 1.85, 10.6, '"yes"', "#15803d")
side_label(cx - 1.5, 10.6, '"no" →\ncancel', "#dc2626")

# ─────────────────────────────────────────────────────────────────────────────
# RESPONSE NODE (shared convergence)
# ─────────────────────────────────────────────────────────────────────────────
box(6.5, 8.75, 2.6, 0.72, CLR["response"], "response_node",
    "format reply (LLM or pass-through)", border="#475569", lw=2)

# All branches converge here
converge_from = [
    (BX["create"],  9.5),
    (BX["read"],    11.98),
    (BX["cu"],      12.02),
    (BX["cu"],      11.02),
    (BX["update"],  9.5),
    (BX["delete"],  9.5),
]
for bx, by in converge_from:
    arrow(bx, by, 6.5, 9.11, color="#94a3b8", lw=1.2)

# ─────────────────────────────────────────────────────────────────────────────
# END
# ─────────────────────────────────────────────────────────────────────────────
circle(6.5, 7.85, "END")
arrow(6.5, 8.39, 6.5, 8.17)

# ─────────────────────────────────────────────────────────────────────────────
# MULTI-TURN LOOP annotation
# ─────────────────────────────────────────────────────────────────────────────
ax.annotate("",
    xy=(6.5, 14.14), xytext=(6.5, 7.85),
    arrowprops=dict(arrowstyle="-|>", color="#3b82f6", lw=1.5,
                    linestyle="dashed",
                    connectionstyle="arc3,rad=0.55"),
    zorder=2)
ax.text(12.4, 11.0,
        "Multi-turn loop:\nawait = set\nnext HTTP request\nresumes here",
        ha="center", fontsize=7.5, color="#3b82f6", style="italic",
        bbox=dict(fc="#eff6ff", ec="#3b82f6", pad=4, boxstyle="round"),
        zorder=6)

# ─────────────────────────────────────────────────────────────────────────────
# LEGEND
# ─────────────────────────────────────────────────────────────────────────────
legend_items = [
    (CLR["io"],       "#374151", "I/O node"),
    (CLR["intent"],   "#7c3aed", "LLM call"),
    (CLR["create"],   "#15803d", "CREATE branch"),
    (CLR["read"],     "#1d4ed8", "READ branch"),
    (CLR["update"],   "#c2410c", "UPDATE branch"),
    (CLR["delete"],   "#dc2626", "DELETE branch"),
    (CLR["exec"],     "#15803d", "MCP tool call"),
    (CLR["misc"],     "#94a3b8", "cancel / unknown"),
    (CLR["response"], "#475569", "response formatter"),
]
lx, ly = 0.25, 7.2
ax.text(lx, ly + 0.35, "Legend", fontsize=9, fontweight="bold", color="#1e293b")
for fc, ec, label in legend_items:
    r = FancyBboxPatch((lx, ly - 0.15), 0.4, 0.28,
                       boxstyle="round,pad=0.02,rounding_size=0.06",
                       linewidth=1, edgecolor=ec, facecolor=fc, zorder=6)
    ax.add_patch(r)
    ax.text(lx + 0.55, ly - 0.01, label,
            va="center", fontsize=8, color="#1e293b", zorder=6)
    ly -= 0.42

plt.tight_layout(pad=0.3)
fig.savefig(OUT, dpi=160, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Saved {OUT}")
