from pathlib import Path


def save_figure(fig, name, figures_dir):
    path = Path(figures_dir) / name
    fig.savefig(path, dpi=300, bbox_inches="tight")
    return path