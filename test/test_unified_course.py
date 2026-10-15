import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import assemble_course as course
class UnifiedCourseTests(unittest.TestCase):
 def test_wrapped_questions_keep_the_full_prompt(self):
  self.assertEqual(course.prompts('Context.\n\n1. Which period\n   does this dataset cover?\n\n2. Who reports?'), ['Which period does this dataset cover?', 'Who reports?'])
 def test_all_dependencies_and_canonical_names(self):course.validate(course.OUTPUT/'notebooks')
 def test_single_sequence_and_complete_source_map(self):
  self.assertEqual(sorted(p.name for p in course.OUTPUT.iterdir()),['notebooks'])
  self.assertEqual(len(list((course.OUTPUT/'notebooks').glob('*.ipynb'))),22)
  self.assertEqual(len(list((course.OUTPUT/'notebooks/r').glob('*.ipynb'))),6)
  mapping=json.loads((course.ROOT/'docs/audit/unified-course-coverage.json').read_text())
  self.assertEqual(len(mapping),20)
  self.assertEqual(len({r['source'] for r in mapping}),20)
 def test_attribution_only_in_start_references_and_no_ucsf_folder(self):
  self.assertFalse(any(p.is_dir() and 'ucsf' in p.name.lower() for p in course.OUTPUT.rglob('*')))
  for p in course.OUTPUT.rglob('*.ipynb'):
   doc=course.read(p)
   for c in doc['cells']:
    if 'UCSF' in course.text(c):
     self.assertEqual(p.stem,'u00-n00-start-here')
     self.assertTrue(course.text(c).startswith('## References'))
 def test_quizzes_fields_and_stable_assessment_ids(self):
  for u in [1,2,4,5,7]:
   p=next((course.OUTPUT/'notebooks').glob(f'u{u:02d}-n01-*.ipynb'));d=course.read(p)
   self.assertTrue(any(f'choose answers for Unit {u}.' in course.text(c) for c in d['cells']))
  source=course.read(course.SOURCE/'exercises/python/u03-n02-explore-dataset.ipynb')
  merged=course.read(course.OUTPUT/'notebooks/u03-n02-explore-dataset.ipynb')
  self.assertEqual(source['metadata']['al'],merged['metadata']['al'])
if __name__=='__main__':unittest.main()
