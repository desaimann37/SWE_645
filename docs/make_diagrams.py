import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

# ─────────────────────────────────────────────────────────────
# DIAGRAM 1 — System Architecture
# ─────────────────────────────────────────────────────────────

def draw_arch():
    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.5)
    ax.axis("off")
    fig.patch.set_facecolor("#fafafa")

    # ── color palette ──────────────────────────────────────────
    C_BROWSER  = "#dbeafe"   # light blue
    C_REACT    = "#dbeafe"
    C_AGENT    = "#ede9fe"   # light purple
    C_MCP      = "#dcfce7"   # light green
    C_DB       = "#fef9c3"   # light yellow
    C_KUBE     = "#f0f4f8"   # very light grey for K8s pod box
    C_BORDER   = "#374151"
    C_ARROW    = "#6b7280"
    C_TITLE    = "#1e293b"
    C_LABEL    = "#374151"
    C_POD_BDR  = "#9ca3af"
    C_POD_FILL = "#f8fafc"

    def box(ax, x, y, w, h, color, label, sublabel="", radius=0.25,
            border="#374151", lw=1.4, fontsize=10.5, subfontsize=8.5):
        rect = FancyBboxPatch((x, y), w, h,
                              boxstyle=f"round,pad=0.05,rounding_size={radius}",
                              linewidth=lw, edgecolor=border,
                              facecolor=color, zorder=3)
        ax.add_patch(rect)
        cy = y + h / 2 + (0.18 if sublabel else 0)
        ax.text(x + w / 2, cy, label,
                ha="center", va="center", fontsize=fontsize,
                fontweight="bold", color=C_TITLE, zorder=4)
        if sublabel:
            ax.text(x + w / 2, y + h / 2 - 0.22, sublabel,
                    ha="center", va="center", fontsize=subfontsize,
                    color="#6b7280", zorder=4, style="italic")

    def pod_container(ax, x, y, w, h, label):
        rect = FancyBboxPatch((x, y), w, h,
                              boxstyle="round,pad=0.05,rounding_size=0.2",
                              linewidth=1.2, edgecolor=C_POD_BDR,
                              facecolor=C_POD_FILL,
                              linestyle="--", zorder=2)
        ax.add_patch(rect)
        ax.text(x + 0.15, y + h - 0.28, label,
                ha="left", va="top", fontsize=7.5,
                color="#9ca3af", fontweight="bold",
                fontfamily="monospace", zorder=4)

    def arrow(ax, x1, y1, x2, y2, label="", color=C_ARROW):
        ax.annotate("",
                    xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(
                        arrowstyle="-|>",
                        color=color,
                        lw=1.6,
                        connectionstyle="arc3,rad=0.0",
                    ), zorder=5)
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx, my + 0.18, label,
                    ha="center", va="bottom", fontsize=7.5,
                    color="#6b7280", style="italic", zorder=6,
                    bbox=dict(fc="#fafafa", ec="none", pad=1))

    # ── Title ─────────────────────────────────────────────────
    ax.text(6.5, 7.15, "System Architecture — Agentic Student Survey",
            ha="center", va="center", fontsize=14, fontweight="bold",
            color=C_TITLE)
    ax.text(6.5, 6.82, "Three-pod Kubernetes deployment with LangGraph AI Agent + FastMCP Tool Server",
            ha="center", va="center", fontsize=9, color="#6b7280")

    # ── Browser ───────────────────────────────────────────────
    box(ax, 0.3, 3.1, 1.8, 1.2, "#f1f5f9", "Browser",
        "User", border="#94a3b8", fontsize=10)

    # ── K8s cluster boundary ───────────────────────────────────
    kube_rect = FancyBboxPatch((2.4, 0.4), 8.5, 6.0,
                                boxstyle="round,pad=0.1,rounding_size=0.3",
                                linewidth=2.0, edgecolor="#3b82f6",
                                facecolor="#f0f7ff", linestyle="-", zorder=1)
    ax.add_patch(kube_rect)
    ax.text(2.65, 6.22, "Kubernetes Cluster",
            ha="left", va="top", fontsize=9, fontweight="bold",
            color="#3b82f6", zorder=4)

    # ── Pod 1 — Frontend ───────────────────────────────────────
    pod_container(ax, 2.65, 3.85, 2.6, 2.25, "Pod 1")
    box(ax, 2.85, 4.55, 2.2, 1.2, C_REACT,
        "React Frontend", "Nginx  •  port 80", fontsize=10)
    ax.text(3.95, 4.25, "Chat UI + Survey Forms",
            ha="center", fontsize=7.5, color="#6b7280", zorder=4)

    # ── Pod 2 — Agent ─────────────────────────────────────────
    pod_container(ax, 2.65, 0.7, 2.6, 2.85, "Pod 2")
    box(ax, 2.85, 1.9, 2.2, 1.25, C_AGENT,
        "LangGraph Agent", "FastAPI  •  port 9000", fontsize=10)
    ax.text(3.95, 1.65, "Claude Haiku 4.5",
            ha="center", fontsize=7.5, color="#6b7280", zorder=4)
    ax.text(3.95, 1.37, "Intent  •  Extract  •  Confirm",
            ha="center", fontsize=7.2, color="#9ca3af", zorder=4)

    # ── Pod 3 — Backend / MCP ──────────────────────────────────
    pod_container(ax, 6.05, 0.7, 2.95, 2.85, "Pod 3")
    box(ax, 6.25, 1.9, 2.55, 1.25, C_MCP,
        "FastAPI + FastMCP", "port 8000  •  /mcp", fontsize=10)
    ax.text(7.52, 1.65, "6 MCP Tools",
            ha="center", fontsize=7.5, color="#6b7280", zorder=4)
    ax.text(7.52, 1.37, "create  search  update  delete",
            ha="center", fontsize=7.2, color="#9ca3af", zorder=4)

    # ── Database ───────────────────────────────────────────────
    box(ax, 9.8, 1.82, 2.55, 1.4, C_DB,
        "MySQL RDS", "AWS  •  port 3306",
        border="#b45309", fontsize=10)
    ax.text(11.07, 1.6, "studentsurvey DB",
            ha="center", fontsize=7.5, color="#92400e", zorder=4)

    # ── K8s Secret ────────────────────────────────────────────
    sec_rect = FancyBboxPatch((6.25, 3.8), 2.55, 0.95,
                               boxstyle="round,pad=0.05,rounding_size=0.18",
                               linewidth=1.1, edgecolor="#dc2626",
                               facecolor="#fff1f2", linestyle="-.", zorder=3)
    ax.add_patch(sec_rect)
    ax.text(7.52, 4.28, "K8s Secret",
            ha="center", va="center", fontsize=9.5,
            fontweight="bold", color="#dc2626", zorder=4)
    ax.text(7.52, 4.0, "ANTHROPIC_API_KEY  •  DATABASE_URL",
            ha="center", va="center", fontsize=7, color="#dc2626", zorder=4)

    # ── Arrows ────────────────────────────────────────────────
    # Browser → Frontend
    arrow(ax, 2.1, 3.72, 2.85, 4.55, "HTTP / browser")

    # Frontend → Agent
    arrow(ax, 3.95, 3.85, 3.95, 3.15, "POST /agent/query")

    # Agent → Backend MCP
    arrow(ax, 5.07, 2.52, 6.25, 2.52, "MCP over HTTP")

    # Backend → RDS
    arrow(ax, 8.8, 2.52, 9.8, 2.52, "SQLModel / MySQL")

    # Secret → Agent (dashed)
    ax.annotate("",
                xy=(3.95, 3.15), xytext=(6.25, 4.28),
                arrowprops=dict(arrowstyle="-|>", color="#dc2626",
                                lw=1.1, linestyle="dashed",
                                connectionstyle="arc3,rad=0.15"),
                zorder=5)
    ax.text(5.1, 4.05, "injects secrets", fontsize=7,
            color="#dc2626", style="italic", ha="center", zorder=6)

    # ── Legend ────────────────────────────────────────────────
    legend_items = [
        (C_REACT,  "#374151", "React Frontend (Pod 1)"),
        (C_AGENT,  "#374151", "LangGraph Agent (Pod 2)"),
        (C_MCP,    "#374151", "FastAPI + MCP Backend (Pod 3)"),
        (C_DB,     "#b45309", "MySQL RDS (AWS)"),
    ]
    lx, ly = 0.3, 2.65
    for fc, ec, label in legend_items:
        r = FancyBboxPatch((lx, ly), 0.35, 0.22,
                            boxstyle="round,pad=0.02,rounding_size=0.05",
                            linewidth=1.0, edgecolor=ec, facecolor=fc, zorder=6)
        ax.add_patch(r)
        ax.text(lx + 0.45, ly + 0.11, label,
                va="center", fontsize=7.5, color=C_LABEL, zorder=6)
        ly -= 0.35

    plt.tight_layout(pad=0.3)
    fig.savefig("arch-diagram.png", dpi=180, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("arch-diagram.png saved")


# ─────────────────────────────────────────────────────────────
# DIAGRAM 2 — LangGraph Workflow
# ─────────────────────────────────────────────────────────────

def draw_langgraph():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis("off")
    fig.patch.set_facecolor("#fafafa")

    C_START   = "#1e293b"
    C_IO      = "#dbeafe"
    C_INTENT  = "#ede9fe"
    C_CREATE  = "#bbf7d0"
    C_READ    = "#bfdbfe"
    C_UPDATE  = "#fed7aa"
    C_DELETE  = "#fecaca"
    C_RESP    = "#f1f5f9"
    C_EXEC    = "#a7f3d0"
    C_END     = "#1e293b"
    C_BORDER  = "#374151"

    def node(ax, x, y, w, h, color, text, sub="", radius=0.22,
             border=C_BORDER, lw=1.4, fs=9.5, sfs=7.8, bold=True):
        r = FancyBboxPatch((x - w/2, y - h/2), w, h,
                           boxstyle=f"round,pad=0.04,rounding_size={radius}",
                           linewidth=lw, edgecolor=border,
                           facecolor=color, zorder=3)
        ax.add_patch(r)
        dy = 0.14 if sub else 0
        ax.text(x, y + dy, text,
                ha="center", va="center", fontsize=fs,
                fontweight="bold" if bold else "normal",
                color="#1e293b", zorder=4)
        if sub:
            ax.text(x, y - 0.18, sub,
                    ha="center", va="center", fontsize=sfs,
                    color="#6b7280", style="italic", zorder=4)

    def circle(ax, x, y, r, color, text, fs=9, fw="bold"):
        c = plt.Circle((x, y), r, color=color, zorder=3)
        ax.add_patch(c)
        ax.text(x, y, text, ha="center", va="center",
                fontsize=fs, fontweight=fw, color="white", zorder=4)

    def arr(ax, x1, y1, x2, y2, label="", color="#6b7280",
            rad=0.0, lw=1.5, fs=7.5):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(
                        arrowstyle="-|>", color=color, lw=lw,
                        connectionstyle=f"arc3,rad={rad}"),
                    zorder=5)
        if label:
            mx = (x1+x2)/2 + (0.18 if rad > 0 else 0)
            my = (y1+y2)/2
            ax.text(mx, my, label, ha="center", va="center",
                    fontsize=fs, color="#6b7280", style="italic",
                    bbox=dict(fc="#fafafa", ec="none", pad=1), zorder=6)

    def dashed_arr(ax, x1, y1, x2, y2, label="", color="#94a3b8", fs=7):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(
                        arrowstyle="-|>", color=color, lw=1.2,
                        linestyle="dashed"),
                    zorder=5)
        if label:
            ax.text((x1+x2)/2, (y1+y2)/2 + 0.13, label,
                    ha="center", va="center", fontsize=fs,
                    color=color, style="italic", zorder=6)

    # ── Title ─────────────────────────────────────────────────
    ax.text(7, 8.72, "LangGraph Agent Workflow",
            ha="center", va="center", fontsize=14,
            fontweight="bold", color="#1e293b")
    ax.text(7, 8.42, "Intent classification → CRUD branch → human-in-the-loop confirmation → response",
            ha="center", va="center", fontsize=8.5, color="#6b7280")

    # ── START / END ───────────────────────────────────────────
    circle(ax, 7, 8.05, 0.28, "#1e293b", "S", fs=9)
    circle(ax, 7, 0.42, 0.28, "#1e293b", "E", fs=9)

    # ── Top spine: input → intent ──────────────────────────────
    node(ax, 7, 7.42, 1.7, 0.52, C_IO, "input", "receive user message")
    node(ax, 7, 6.6,  2.1, 0.6,  C_INTENT, "intent",
         "LLM classifies intent", border="#7c3aed", lw=1.8)

    arr(ax, 7, 7.77, 7, 7.68)
    arr(ax, 7, 7.16, 7, 6.9)

    # ── Branch column positions ───────────────────────────────
    cols = {"create": 1.85, "read": 4.55, "update": 9.45, "delete": 12.15}
    branch_y_top = 5.95

    # Branch labels below intent box
    for name, cx in cols.items():
        ax.text(cx, 6.18, name, ha="center", fontsize=8,
                color="#6b7280", style="italic")
        arr(ax, 7, 6.3, cx, branch_y_top, color="#9ca3af")

    # ─── CREATE branch ────────────────────────────────────────
    cx = cols["create"]
    node(ax, cx, 5.45, 2.1, 0.75, C_CREATE, "create_extract",
         "extract fields from input")
    node(ax, cx, 4.5,  2.1, 0.75, C_CREATE, "create_ask_or_confirm",
         "ask missing / summarize")
    node(ax, cx, 3.45, 2.0, 0.65, "#f0fdf4", "awaiting confirm",
         border="#16a34a", lw=1.1)
    node(ax, cx, 2.5,  2.1, 0.75, C_EXEC,   "create_execute",
         "call create_survey()", border="#15803d", lw=1.6)

    arr(ax, cx, branch_y_top, cx, 5.83)
    arr(ax, cx, 5.08, cx, 4.88)
    arr(ax, cx, 4.12, cx, 3.78)
    arr(ax, cx, 3.12, cx, 2.88)

    ax.text(cx + 1.2, 3.9, "\"yes\"", fontsize=7.5, color="#16a34a",
            style="italic")
    ax.text(cx - 1.55, 3.9, "\"no\" → cancel", fontsize=7,
            color="#dc2626", style="italic")

    # ─── READ branch ──────────────────────────────────────────
    cx = cols["read"]
    node(ax, cx, 5.28, 2.0, 0.75, C_READ, "read_execute",
         "call search_surveys()")

    arr(ax, cx, branch_y_top, cx, 5.66)

    # ─── UPDATE branch ────────────────────────────────────────
    cx = cols["update"]
    node(ax, cx, 5.45, 2.1, 0.75, C_UPDATE, "update_resolve",
         "identify target survey")
    node(ax, cx, 4.5,  2.1, 0.75, C_UPDATE, "update confirm",
         "show proposed changes", border="#c2410c", lw=1.1)
    node(ax, cx, 3.45, 2.0, 0.65, "#fff7ed", "awaiting confirm",
         border="#c2410c", lw=1.1)
    node(ax, cx, 2.5,  2.1, 0.75, C_EXEC,   "update_execute",
         "call update_survey()", border="#15803d", lw=1.6)

    arr(ax, cx, branch_y_top, cx, 5.83)
    arr(ax, cx, 5.08, cx, 4.88)
    arr(ax, cx, 4.12, cx, 3.78)
    arr(ax, cx, 3.12, cx, 2.88)

    # ─── DELETE branch ────────────────────────────────────────
    cx = cols["delete"]
    node(ax, cx, 5.45, 2.1, 0.75, C_DELETE, "delete_resolve",
         "find survey by name/ID")
    node(ax, cx, 4.5,  2.1, 0.75, C_DELETE, "delete confirm",
         "show survey details", border="#dc2626", lw=1.6)
    node(ax, cx, 3.45, 2.0, 0.65, "#fff1f2", "awaiting confirm",
         border="#dc2626", lw=1.3)
    node(ax, cx, 2.5,  2.1, 0.75, C_EXEC,   "delete_execute",
         "call delete_survey()", border="#15803d", lw=1.6)

    arr(ax, cx, branch_y_top, cx, 5.83)
    arr(ax, cx, 5.08, cx, 4.88)
    arr(ax, cx, 4.12, cx, 3.78)
    arr(ax, cx, 3.12, cx, 2.88)

    # ─── Response node (shared) ───────────────────────────────
    node(ax, 7, 1.5, 2.3, 0.65, C_RESP, "response",
         "format & return to user", border="#475569", lw=1.6)

    # All branches converge to response
    for name, bx in cols.items():
        exec_y = 2.12
        arr(ax, bx, exec_y, 7, 1.83, color="#94a3b8")
    # Read goes directly
    arr(ax, cols["read"], 4.9, 7, 1.83, color="#94a3b8")

    arr(ax, 7, 1.17, 7, 0.70)

    # ─── cancel / unknown side nodes ──────────────────────────
    node(ax, 7, 5.5, 1.6, 0.5, "#f1f5f9", "cancel / unknown",
         border="#94a3b8", lw=1.0, fs=8.5)
    arr(ax, 7, 6.3, 7, 5.75, color="#94a3b8")
    arr(ax, 7, 5.25, 7, 1.83, color="#94a3b8")

    # ─── Legend ───────────────────────────────────────────────
    lx, ly = 0.15, 2.2
    items = [
        (C_CREATE, "#374151", "CREATE branch"),
        (C_READ,   "#374151", "READ branch"),
        (C_UPDATE, "#374151", "UPDATE branch"),
        (C_DELETE, "#374151", "DELETE branch"),
        (C_EXEC,   "#15803d", "MCP tool call"),
    ]
    ax.text(lx, ly + 0.3, "Legend", fontsize=8.5, fontweight="bold",
            color="#374151")
    for fc, ec, label in items:
        ly -= 0.42
        r = FancyBboxPatch((lx, ly), 0.38, 0.26,
                            boxstyle="round,pad=0.02,rounding_size=0.06",
                            linewidth=1, edgecolor=ec, facecolor=fc, zorder=6)
        ax.add_patch(r)
        ax.text(lx + 0.5, ly + 0.13, label,
                va="center", fontsize=7.8, color="#374151", zorder=6)

    plt.tight_layout(pad=0.2)
    fig.savefig("langgraph-diagram.png", dpi=180, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("langgraph-diagram.png saved")


draw_arch()
draw_langgraph()
print("Both diagrams generated.")
