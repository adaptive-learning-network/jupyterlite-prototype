import copy,contextlib,io,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import make_units09_14 as m
class NarrativeTests(unittest.TestCase):
 def test_every_criterion_and_emitted_check(self):
  for spec in m.UNITS:
   u=spec['unit'];answer=m.expected_answers(u,m.DATA)
   self.assertEqual(m.evaluate_answer(u,None,m.DATA),'incomplete')
   self.assertEqual(m.evaluate_answer(u,answer,m.DATA),'correct')
   for key,value in answer.items():
    with self.subTest(unit=u,key=key):
     partial={**answer,key:None};self.assertEqual(m.evaluate_answer(u,partial,m.DATA),'incomplete')
     wrong={**answer,key:value+1 if type(value) is int else ['wrong'] if isinstance(value,list) else 'wrong'}
     self.assertEqual(m.evaluate_answer(u,wrong,m.DATA),'incorrect')
   ident=f"u{u:02d}-{spec['slug']}"
   for response,outcome in [(None,'incomplete'),(wrong,'incorrect'),(wrong,'incorrect'),(answer,'correct')]:
    stream=io.StringIO()
    with contextlib.redirect_stdout(stream):
     exec((m.ROOT/'app-assets/adaptive-learning/checks'/f'{ident}.py').read_text(encoding='utf-8'),{f'unit{u:02d}_response':response})
    self.assertEqual(json.loads(stream.getvalue().split('AL_OBSERVATION ')[1])['outcome'],outcome)
 def test_dictionary_and_keys(self):
  art=m.build_artifact(9,m.expected_answers(9,m.DATA),m.DATA)
  self.assertIsNone(art['Value reconciliation'][-1]['value'])
  self.assertEqual(art['Value reconciliation'][-1]['action'],'review required')
  good=m.expected_answers(10,m.DATA)
  self.assertTrue(m.build_artifact(10,good,m.DATA)['Key audit'][0]['unique'])
  self.assertFalse(m.build_artifact(10,{**good,'key':'district'},m.DATA)['Key audit'][0]['unique'])
 def test_transform_boundary_missing_and_identity(self):
  data=copy.deepcopy(m.DATA);data['cases'][0]['age']=5;data['cases'][1]['age']=None
  original=copy.deepcopy(data)
  answer=m.expected_answers(11,data);art=m.build_artifact(11,answer,data)
  self.assertEqual(art['Transformed copy'][0]['age_group'],'5plus')
  self.assertEqual(art['Transformed copy'][1]['age_group'],'unknown')
  self.assertTrue(art['Reconciliation'][0]['same_ID_multiplicity'])
  bad=m.build_artifact(11,{**answer,'missing':'drop'},data)
  self.assertTrue(bad['Reconciliation'][0]['same_ID_multiplicity'])
  self.assertEqual(m.evaluate_answer(11,{**answer,'missing':'drop'},data),'incorrect')
  self.assertEqual(answer['case_group'],'5plus')
  self.assertEqual(m.age_group(4),'under5')
  self.assertEqual(m.age_group(5),'5plus')
  self.assertEqual(m.age_group(8),'5plus')
  self.assertEqual(m.age_group(None),'unknown')
  self.assertEqual(data,original)
 def test_link_rejects_conflicts_unknowns_and_unmatched(self):
  art=m.build_artifact(12,m.expected_answers(12,m.DATA),m.DATA)
  self.assertEqual(len(art['Linked case view']),4)
  self.assertEqual([r['result'] for r in art['Linked case view']],['positive','conflict','unmatched','unmatched'])
  self.assertEqual([r['case_id'] for r in art['Candidate exchange rows']],['C01'])
  self.assertEqual(sum(r['accepted'] for r in art['Import validation']),1)
  bad=m.build_artifact(12,{'join':'inner','conflicts':1,'unknown':'send'},m.DATA)
  self.assertEqual(len(bad['Linked case view']),2)
  self.assertEqual(bad['Candidate exchange rows'],art['Candidate exchange rows'])
 def test_computed_analysis_and_review(self):
  self.assertEqual(m.summarize(m.DATA)['onset'],{'2021-10-18':1,'2021-10-19':1,'2021-10-20':2})
  art=m.build_artifact(13,m.expected_answers(13,m.DATA),m.DATA)
  self.assertEqual(art['District briefing'][0]['share_of_reports'],0.75)
  self.assertEqual([r['cases'] for r in art['Time summary']],[1,1,2])
  data=copy.deepcopy(m.DATA);data['cases'].pop(0)
  self.assertEqual(m.expected_answers(13,data)['kambia'],2)
  self.assertNotIn('counts',m.expected_answers(14,data)['supported'])
  review=m.build_artifact(14,m.expected_answers(14,m.DATA),m.DATA)
  self.assertEqual([r['your_decision'] for r in review['Draft review']],['supported','not supported','not supported','supported'])
 def test_generated_cells_compile_and_are_local(self):
  for s in m.UNITS:
   doc=json.loads((m.ROOT/f"content/exercises/python/u{s['unit']:02d}-n01-{s['slug']}.ipynb").read_text(encoding='utf-8'))
   for cell in doc['cells']:
    source=''.join(cell['source'])
    if cell['cell_type']=='code':compile(source,'notebook','exec',flags=__import__('ast').PyCF_ALLOW_TOP_LEVEL_AWAIT)
   self.assertTrue(''.join(doc['cells'][-1]['source']).startswith('## References'))
   self.assertEqual(len(doc['cells'][0]['attachments']),1)
if __name__=='__main__':unittest.main()
