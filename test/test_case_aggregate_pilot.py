import contextlib,io,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from case_aggregate_widgets import check_code,POLICY_PATH

class ClassificationPilot(unittest.TestCase):
 def check(self,task,answers):
  output=io.StringIO()
  with contextlib.redirect_stdout(output):exec(check_code(),{'classification_response':{'taskId':task,'answers':answers}})
  return json.loads(output.getvalue().split('AL_OBSERVATION ')[1])
 def test_case_numbers_and_summary_identifiers_do_not_change_row_meaning(self):
  first=self.check('new-case-1',{'a':'case','b':'aggregate','c':'case'})
  second=self.check('new-case-2',{'a':'aggregate','b':'case','c':'aggregate'})
  self.assertEqual(first['outcome'],'correct');self.assertEqual(second['outcome'],'correct')
 def test_per_table_feedback_identifies_the_missed_criterion(self):
  result=self.check('new-case-1',{'a':'aggregate','b':'aggregate','c':'case'})
  self.assertEqual(result['outcome'],'incorrect')
  self.assertEqual([r['id'] for r in result['criteria'] if r['outcome']=='incorrect'],['a'])
 def test_partial_answers_are_incomplete(self):
  result=self.check('practice',{'a':'case'})
  self.assertEqual(result['outcome'],'incomplete')
  self.assertEqual(len([r for r in result['criteria'] if r['outcome']=='incomplete']),4)
 def test_practice_and_new_cases_share_no_example_rows(self):
  tasks=json.loads(POLICY_PATH.read_text(encoding='utf-8'))['tasks']
  examples=[{tuple(row) for table in task['tables'] for row in table['rows']} for task in tasks]
  for i,rows in enumerate(examples):
   for other in examples[i+1:]:self.assertFalse(rows & other)
if __name__=='__main__':unittest.main()
