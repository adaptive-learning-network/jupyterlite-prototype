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
 def test_canonical_reflection_questions_have_registered_stable_ids(self):
  import ast
  registry=json.loads((course.ROOT/'scripts/reflection_questions.json').read_text(encoding='utf-8'))
  for path in (course.OUTPUT/'notebooks').glob('*.ipynb'):
   for cell in course.read(path)['cells']:
    source=course.text(cell)
    if cell['cell_type']!='code' or '_reflection_section(' not in source:continue
    tree=ast.parse(source.replace('await piplite.install','piplite.install'))
    call=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_reflection_section')
    section,questions=[ast.literal_eval(arg) for arg in call.args]
    known={(q['id'],q['version']) for q in registry[section]}
    self.assertEqual(len({q['id'] for q in questions}),len(questions))
    for question in questions:self.assertIn((question['id'],question['version']),known,path.name)
 def test_complete_clickable_route_and_intentional_submission(self):
  folder=course.OUTPUT/'notebooks'
  start=course.read(folder/'u00-n00-start-here.ipynb')
  contents=''.join(course.text(c) for c in start['cells'])
  for index,name in enumerate(course.SEQUENCE):
   self.assertIn(f']({name}.ipynb)',contents)
   doc=course.read(folder/(name+'.ipynb'))
   nav=next(c for c in doc['cells'] if c['id']=='continue')
   onward=course.SEQUENCE[index+1] if index+1<len(course.SEQUENCE) else 'u03-n08-my-learning-record'
   self.assertIn(f']({onward}.ipynb)',course.text(nav))
   for cell in doc['cells']:
    if cell.get('metadata',{}).get('al',{}).get('check'):
     self.assertEqual(cell['metadata']['al']['submission'],'widget',name)
 def test_no_imported_procedural_questions_or_second_dataset(self):
  folder=course.OUTPUT/'notebooks'
  for path in folder.glob('*.ipynb'):
   text=''.join(course.text(c) for c in course.read(path)['cells'])
   for bad in ['Answer Question #3','Answer Questions 4 and 5','These are easy to follow, step by step instructions','Then use Excel to fix']:
    self.assertNotIn(bad,text,path.name)
  explore=''.join(course.text(c) for c in course.read(folder/'u03-n02-explore-dataset.ipynb')['cells'])
  self.assertNotIn('laila-case-register.csv',explore)
  self.assertNotIn('8,500',explore)
if __name__=='__main__':unittest.main()
