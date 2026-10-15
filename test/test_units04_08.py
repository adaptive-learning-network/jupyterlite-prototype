"""Native scenario harness for all five generated narratives and their checks."""
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from make_units04_08 import DATA, UNITS, build_artifact, evaluate_answer, expected_answers


class NewNarratives(unittest.TestCase):
    def check(self, spec, response):
        code = (ROOT / "app-assets/adaptive-learning/checks" / f"u{spec['unit']:02d}-{spec['slug']}.py").read_text(encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(code, {f"unit{spec['unit']:02d}_response": response})
        return json.loads(output.getvalue().split("AL_OBSERVATION ")[-1])["outcome"]

    def test_each_check_distinguishes_missing_wrong_each_criterion_and_correct(self):
        for spec in UNITS:
            with self.subTest(unit=spec["unit"]):
                answer = expected_answers(spec["unit"], DATA)
                self.assertEqual(self.check(spec, None), "incomplete")
                self.assertEqual(self.check(spec, answer), "correct")
                for key, value in answer.items():
                    wrong = copy.deepcopy(answer)
                    wrong[key] = ["not-a-valid-option"] if isinstance(value, list) else value + 1 if isinstance(value, int) else "wrong"
                    self.assertEqual(self.check(spec, wrong), "incorrect", key)
                    partial = copy.deepcopy(answer)
                    partial[key] = None
                    self.assertEqual(self.check(spec, partial), "incomplete", key)

    def test_source_join_retains_unknown_not_negative(self):
        joined = build_artifact(4, expected_answers(4, DATA), DATA)
        self.assertEqual(len(joined), len(DATA["cases"]))
        self.assertEqual(sum(row["result"] == "unknown" for row in joined), 2)
        incomplete = build_artifact(4, {"sources": ["case"], "grain": "case"}, DATA)
        self.assertTrue(all(row["result"] == "unknown" for row in incomplete))

    def test_release_uses_counts_and_the_explicit_training_threshold(self):
        released = build_artifact(5, expected_answers(5, DATA), DATA)
        self.assertEqual({row["district"]: row["public_count"] for row in released["Public summary"]}, {"Kambia": 3, "Port Loko": "withheld"})
        self.assertTrue(all(set(row) == set(DATA["task_fields"]) for row in released["Internal extract (invented records)"]))
        denied = build_artifact(5, {"fields": ["case_id", "contact_label"], "suppress": ["Port Loko"]}, DATA)
        self.assertTrue(all(set(row) == {"case_id"} for row in denied["Internal extract (invented records)"]))

    def test_ai_evidence_summary_matches_underlying_rows(self):
        summary = build_artifact(6, {}, DATA)
        self.assertEqual([row["count"] for row in summary], [4, 1, 1, 2])
        changed = copy.deepcopy(DATA)
        changed["lab"].append({"case_id": "C03", "result": "positive"})
        self.assertEqual([row["count"] for row in build_artifact(6, {}, changed)], [4, 2, 1, 1])

    def test_validator_accepts_valid_rejects_invalid_and_exposes_lax_rule(self):
        response = expected_answers(7, DATA)
        self.assertEqual([row["accepted"] for row in build_artifact(7, response, DATA)], [True, False, False, False, False, False])
        response["age_max"] = 999
        self.assertTrue(build_artifact(7, response, DATA)[2]["accepted"])
        self.assertEqual(evaluate_answer(7, response, DATA), "incorrect")
        for age in [None, True, "8", 8.5, -1, 121]:
            changed = copy.deepcopy(DATA)
            changed["submissions"][0]["age"] = age
            self.assertFalse(build_artifact(7, expected_answers(7, changed), changed)[0]["accepted"], repr(age))
        optional = expected_answers(7, DATA)
        optional["required"] = ["case_id"]
        self.assertTrue(all(row["accepted"] for row in build_artifact(7, optional, DATA)[-2:]))

    def test_quality_ledger_keeps_originals_and_audit_uses_dates(self):
        original = copy.deepcopy(DATA)
        artifact = build_artifact(8, expected_answers(8, DATA), DATA)
        ledger = artifact["Verified correction log"]
        self.assertEqual(DATA, original)
        self.assertEqual(len(ledger), 3)
        self.assertTrue(all(row["evidence"] for row in ledger))
        self.assertTrue(any(row["before"] == 180 and row["after"] == 18 for row in ledger))
        self.assertEqual(len(artifact["Cleaned copy"]), 4)
        conflict = copy.deepcopy(DATA)
        conflict["dirty"][1]["age"] = 9
        kept = build_artifact(8, expected_answers(8, conflict), conflict)["Cleaned copy"]
        self.assertEqual(sum(row["case_id"] == "Q01" for row in kept), 2, "a conflicting repeated ID must not be silently deduplicated")
        changed = copy.deepcopy(DATA)
        changed["dirty"][-1]["report_date"] = "2021-10-19"
        self.assertEqual(expected_answers(8, changed)["late"], 0)


if __name__ == "__main__":
    unittest.main()
