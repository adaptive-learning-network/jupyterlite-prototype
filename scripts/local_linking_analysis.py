"""Runnable local examples for the integrated U12 and U13 narratives."""
from pprint import pformat

LINK_INPUTS = '''# Run this cell to display the two supplied tables.
import pandas as pd
from IPython.display import display

case_records = pd.DataFrame(CASE_RECORDS)
laboratory_records = pd.DataFrame(LAB_RECORDS)
result_codes = RESULT_CODES
print("Case records")
display(case_records)
print("Laboratory records")
display(laboratory_records)
print("Result codes:", result_codes)
'''

DIRECT_LINK = '''# Run this cell to see why matching alone is not enough.
direct_link = case_records.merge(laboratory_records, on="case_id", how="left")
display(direct_link)
print("Cases before linking:", len(case_records))
print("Rows after this direct link:", len(direct_link))
print("Case identifiers that now appear more than once:",
      direct_link.loc[direct_link["case_id"].duplicated(), "case_id"].tolist())
'''

VALIDATED_LINK = '''# Run this cell to check the laboratory rows before using their results.
lab_review = laboratory_records.copy()
lab_review["known_case"] = lab_review["case_id"].isin(case_records["case_id"])
lab_review["known_code"] = lab_review["code"].isin(result_codes)
lab_review["multiple_lab_rows"] = lab_review["case_id"].duplicated(keep=False)
lab_review["accepted"] = (lab_review["known_case"] & lab_review["known_code"]
                          & ~lab_review["multiple_lab_rows"])
display(lab_review)

accepted_results = lab_review.loc[lab_review["accepted"], ["case_id", "code"]].copy()
accepted_results["result"] = accepted_results["code"].map(result_codes)
linked_cases = case_records.merge(accepted_results[["case_id", "result"]],
                                  on="case_id", how="left", validate="one_to_one")
linked_cases["lab_status"] = linked_cases["result"].fillna("unmatched")
conflicting_ids = lab_review.loc[lab_review["multiple_lab_rows"], "case_id"]
linked_cases.loc[linked_cases["case_id"].isin(conflicting_ids), "lab_status"] = "conflict"
print("Case table after checking the laboratory records")
display(linked_cases)
print("All case identifiers retained:",
      sorted(linked_cases["case_id"]) == sorted(case_records["case_id"]))
print("Rows ready for a possible exchange; nothing is sent")
display(accepted_results)
'''

PLOT_SETUP = '''# Run once to load the locally bundled plotting packages.
try:
    import seaborn as sns
except ImportError:
    import piplite
    await piplite.install("seaborn==0.13.2")
    import seaborn as sns
import io
import base64
import pandas as pd
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
sns.set_theme(style="whitegrid", font_scale=1.05)
from matplotlib.ticker import MaxNLocator
from IPython.display import HTML, display
from html import escape

def show_course_plot(fig, description):
    for ax in fig.axes:
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        tallest = max((bar.get_height() for bar in ax.patches), default=0)
        ax.set_ylim(0, tallest * 1.25 if tallest else 1)
        for bars in ax.containers:
            ax.bar_label(bars, fmt="%d", padding=3)
    fig.tight_layout()
    output = io.BytesIO()
    with matplotlib.rc_context({"svg.fonttype": "none"}):
        fig.savefig(output, format="svg", bbox_inches="tight")
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    display(HTML('<figure style="margin:0;width:100%;">'
                 '<img style="display:block;width:100%;max-width:100%;height:auto;" '
                 'alt="' + escape(description, quote=True) + '" '
                 'src="data:image/svg+xml;base64,' + encoded + '" /></figure>'))
    plt.close(fig)
'''

ANALYSIS_INPUTS = '''# Run this cell to build the analysis table from the supplied records.
cases = pd.DataFrame(CASE_RECORDS)
cases["onset_date"] = pd.to_datetime(cases["onset_date"])
cases["age_group"] = cases["age"].map(
    lambda age: "unknown" if pd.isna(age) else "under5" if age < 5 else "5plus")
display(cases)
'''

PERSON_CODE = '''# Run this cell to summarize person: age and recorded sex.
age_counts = cases.groupby("age_group").size().reindex(
    ["under5", "5plus", "unknown"], fill_value=0).rename("cases").reset_index()
sex_counts = cases.groupby("sex").size().rename("cases").reset_index()
display(age_counts)
display(sex_counts)
fig, ax = plt.subplots(figsize=(5.5, 3.8))
sns.barplot(data=age_counts, x="age_group", y="cases",
            errorbar=None, color="#287d8e", ax=ax)
ax.set(title="Cases by age group", xlabel="Age group", ylabel="Reported cases")
show_course_plot(fig, "Invented reported cases by age group; exact counts are in the table.")
fig, ax = plt.subplots(figsize=(5.5, 3.8))
sns.barplot(data=sex_counts, x="sex", y="cases",
            errorbar=None, color="#287d8e", ax=ax)
ax.set(title="Cases by recorded sex", xlabel="Sex code (F / M)",
       ylabel="Reported cases")
show_course_plot(fig, "Invented reported cases by recorded sex; exact counts are in the table.")

known_ages = cases["age"].dropna()
age_modes = known_ages.mode()
age_statistics = pd.DataFrame({
    "Measure": ["Known ages", "Mean (years)", "Median (years)", "Minimum",
                "Maximum", "Range (years)", "Mode"],
    "Value": [len(known_ages), known_ages.mean(), known_ages.median(),
              known_ages.min(), known_ages.max(), known_ages.max() - known_ages.min(),
              age_modes.iloc[0] if len(age_modes) == 1 else "No single most frequent age"]
})
display(age_statistics)
'''

PLACE_CODE = '''# Run this cell to compare counts and shares of reports by district.
district_counts = cases.groupby("district").size().rename("cases").reset_index()
district_counts["share_of_reports"] = district_counts["cases"] / len(cases)
display(district_counts)
fig, ax = plt.subplots(figsize=(5.5, 3.8))
sns.barplot(data=district_counts, x="district", y="cases",
            errorbar=None, color="#287d8e", ax=ax)
ax.set(title="Reported cases by district", xlabel="Reporting district",
       ylabel="Reported cases")
show_course_plot(fig, "Invented reported case counts by district. These are counts, not population disease rates.")
'''

TIME_CODE = '''# Run this cell to count cases by illness-onset day, including zero-count days.
onset_counts = cases.groupby("onset_date").size().reindex(
    pd.date_range(cases["onset_date"].min(), cases["onset_date"].max(), freq="D"),
    fill_value=0).rename_axis("onset_date").reset_index(name="cases")
onset_counts["day"] = onset_counts["onset_date"].dt.strftime("%d %b %Y")
display(onset_counts[["day", "cases"]])
fig, ax = plt.subplots(figsize=(6, 3.8))
sns.barplot(data=onset_counts, x="day", y="cases",
            errorbar=None, color="#287d8e", ax=ax)
ax.set(title="Cases by onset date",
       xlabel="Illness-onset date (one-day intervals)", ylabel="Reported cases")
show_course_plot(fig, "Invented reported cases by illness-onset day; one-day intervals, including zero-count days.")
'''


def linking_cells(cell, data):
    inputs = LINK_INPUTS.replace('CASE_RECORDS', pformat(data['cases'], width=72, sort_dicts=False)).replace('LAB_RECORDS', pformat(data['lab'], width=72, sort_dicts=False)).replace('RESULT_CODES', repr(data['code_map']))
    return [
        cell('markdown', '## 1. Inspect the two supplied tables\n\nRun the next cell. Compare the `case_id` values and the fields in each table. The case identifier refers to the same case in both tables. The laboratory codes mean `P` = positive, `NEG` = negative, and `PEND` = pending; `X` has no agreed meaning.', 'link-inputs-intro'),
        cell('code', inputs, 'link-inputs'),
        cell('markdown', '## 2. Check what a direct link produces\n\nA **left join** keeps all case records and attaches matching laboratory rows using `case_id`. Run the next cell: C02 appears twice because it has two laboratory rows. Four original cases become five rows. Counting these rows as cases would overcount. Blank laboratory fields for C03 and C04 mean no matching record was supplied; they do not mean a negative test.', 'link-direct-intro'),
        cell('code', DIRECT_LINK, 'link-direct'),
        cell('markdown', '## 3. Review the laboratory rows before using a result\n\nRun the next cell. It checks three things: the case identifier exists in the case table, the result code has a defined meaning, and there is only one laboratory row for that case in this example. C02 has pending and negative entries, with no dates to show their sequence. The example flags this as `conflict` for follow-up; it does not decide which entry is current. C99 is not in the case table and its code is undefined. These rows need follow-up. Multiple laboratory records can be legitimate in practice; resolving them requires specimen and result information that this example does not provide.\n\nThe checked case table keeps one row for each supplied case. Only validated laboratory results enter the separate table of rows ready for a possible exchange. No data are sent to another system.', 'link-validated-intro'),
        cell('code', VALIDATED_LINK, 'link-validated'),
        cell('markdown', '## Review the linking decisions\n\nRun the next cell for the review controls. Use the tables above to choose how to retain cases, count case identifiers with multiple laboratory rows, and decide what to do with unresolved records. Then select **Submit** for feedback.', 'link-controls-intro'),
    ]


def analysis_cells(cell, data):
    return [
        cell('markdown', '## 1. Load Seaborn and the supplied records\n\nRun the next two cells. The first loads locally bundled plotting packages; the first run may take a little longer. The second displays all four invented case records. Each row is one case, and the date is the date of illness onset.', 'analysis-inputs-intro'),
        cell('code', PLOT_SETUP, 'plot-setup', {'jupyter': {'source_hidden': True}}),
        cell('code', ANALYSIS_INPUTS.replace('CASE_RECORDS', pformat(data['cases'], width=72, sort_dicts=False)), 'analysis-inputs'),
        cell('markdown', '## 2. Person: age and recorded sex\n\nRun the next cell. The age groups use the same fixed rule as Unit 11: less than five years, five years or older, or unknown. An empty category has a count of zero. The second chart uses the sex codes supplied in these records.\n\nThe age table also gives the mean, median, minimum, maximum, range, and mode. The range is the oldest age minus the youngest age. When several ages share the highest frequency, there is no single most frequent age. These summaries describe the supplied cases.', 'person-plot-intro'),
        cell('code', PERSON_CODE, 'person-plot'),
        cell('markdown', '## 3. Place: district counts and shares\n\nRun the next cell. The height of each bar is a case count. The share of reports divides that district count by all cases in this extract. Kambia\'s larger count does not establish a higher disease risk: district population sizes and reporting completeness are not supplied. No household locations are available for a map.', 'place-plot-intro'),
        cell('code', PLACE_CODE, 'place-plot'),
        cell('markdown', '## 4. Time: cases by illness-onset day\n\nRun the next cell. Each bar covers one day. Dates are ordered, and any day with no onset in the displayed period is included with a count of zero. These are onset dates, not dates of notification or reporting. The three-day extract alone cannot establish an outbreak or a twelve-month trend. The exact daily counts appear above the chart.', 'time-plot-intro'),
        cell('code', TIME_CODE, 'time-plot'),
        cell('markdown', '## Review the briefing\n\nRun the next cell for the review controls. Use the tables and plots to choose the reported count for Kambia, the denominator for a share of reports, the chart that answers the timing question, and whether a population rate is available. Then select **Submit**. Use the reflection fields to record your finding, supporting evidence, limitations, and recommended action.', 'analysis-controls-intro'),
    ]
