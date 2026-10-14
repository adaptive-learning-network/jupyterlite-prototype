# Practice data dictionary

These **synthetic** records are a small stand-in for the surveillance spreadsheets used in the case study. They are for practicing structure, filtering, quality checks, and case-ID joins. They are not surveillance evidence.

| File | Field | Meaning |
| --- | --- | --- |
| Case register | case_id | Local case identifier; unique in this file |
| Case register | onset_date | Symptom onset date, ISO 8601 |
| Case register | report_date | Date district received report, ISO 8601 |
| Case register | district | North, South, or East (fictional) |
| Case register | sex | F or M |
| Case register | age_years | Age in completed years |
| Case register | case_status | suspected, confirmed, or discarded |
| Case register | vaccinated | yes, no, or unknown |
| Clinical records | case_id | Join key to the case register |
| Clinical records | fever, rash | yes or no |
| Clinical records | specimen_date | Collection date; blank when missing |
| Clinical records | lab_result | positive or pending |

For a report, check the case definition and reporting period before counting records. A left join from the register shows which cases have no matching clinical record.
