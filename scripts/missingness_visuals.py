"""Shared rendering infrastructure and the bounded U03 missingno pilot."""

RENDERER = '''
def show_missingness_matrix(frame, row_labels):
    import io
    import missingno as msno
    import matplotlib
    matplotlib.use("agg")
    import matplotlib.pyplot as plt
    from IPython.display import SVG, display
    fig, ax = plt.subplots(figsize=(7, 3.2))
    msno.matrix(frame, ax=ax, sparkline=False, labels=True, fontsize=10,
                color=(0.12, 0.46, 0.40))
    ax.set_yticks(range(len(frame)), labels=row_labels)
    ax.set_ylabel("Case-event record")
    ax.set_xlabel("Green = recorded; white = missing")
    ax.set_title("Completeness of the retrieved fields", pad=12)
    fig.tight_layout()
    output = io.BytesIO()
    fig.savefig(output, format="svg", bbox_inches="tight")
    svg = output.getvalue().decode("utf-8").replace("<svg ", '<svg role="img" aria-label="Completeness matrix. Green means recorded; white means missing. Exact counts are in the accompanying table." ', 1)
    display(SVG(data=svg))
    plt.close(fig)
'''

LESSON = """## See the missing date: a completeness matrix

The table says which record lacks an onset date. A **missingno matrix** makes that gap visible: each row is a record and each column is a field. **Green means a value is recorded; white means it is missing.** Use the row label to find the same record in Step 4.

Run this optional cell to draw the matrix. The first run loads the locally bundled plotting packages. The supplied code makes a **separate display copy**, turning blank strings into pandas' missing-value marker (`pd.NA`). Otherwise a blank string could look complete to the plotting library. The source records stay unchanged.

**Read the plot:** Which record has a missing rash-onset date? Is its event date also missing? Would a full green column prove that its dates are correct?

This chart shows **completeness**, one aspect of quality. A recorded date could still be wrong, a record could be duplicated, or a report could arrive late. Keep those questions separate. The table below gives exact counts as well as the visual pattern.
"""

PLOT_CODE = '''# Run this supplied cell to visualize completeness; no edits are needed.
try:
    import missingno
except ImportError:
    import piplite
    await piplite.install(["missingno==0.5.2", "seaborn==0.13.2"])
import pandas as pd

# Normalize blanks only in a separate display copy, not in the source records.
quality_view = pd.DataFrame(onset_rows)[["event_date", "onset"]].replace(r"^\\s*$", pd.NA, regex=True)
quality_view.columns = ["Event date", "Rash onset date"]
show_table([
    {"field": field, "missing": int(quality_view[field].isna().sum()), "total": len(quality_view)}
    for field in quality_view.columns
], [("field", "Field"), ("missing", "Missing values"), ("total", "Records")])
show_missingness_matrix(quality_view, [row["event"] for row in onset_rows])
'''
