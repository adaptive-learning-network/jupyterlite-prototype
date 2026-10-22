"""Meaningful checks of supplied computations and common response controls."""
import contextlib,io,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import make_exercises as early
import make_units04_08 as later

class P2Interactions(unittest.TestCase):
 def test_supplied_calculations_match_data_and_count_distinct_children(self):
  for spec in early.EXERCISES[1:4]:
   namespace={}
   with contextlib.redirect_stdout(io.StringIO()):
    exec(early.LOAD['python'],namespace)
    exec(early.scaffold(spec),namespace)
   for key,(_,expected) in spec['variables'].items():self.assertEqual(namespace[key],expected)
   if spec['check']=='coverage':
    self.assertEqual(namespace['numerator'],46)
    self.assertEqual(namespace['denominator'],50)
    self.assertTrue(namespace['matching']['patient_id'].is_unique)
 def test_checkboxes_collect_values_lock_and_allow_keyboard_changes(self):
  namespace={}
  with contextlib.redirect_stdout(io.StringIO()):exec(later.setup_code(later.UNITS[0]).replace('await piplite.install','piplite.install'),namespace)
  control=namespace['controls']['sources']
  control.boxes[0].value=True;control.boxes[1].value=True
  self.assertEqual(namespace['control_answer'](control),['case','lab'])
  control.disabled=True
  self.assertTrue(all(box.disabled for box in control.boxes))
  control.disabled=False;control.boxes[0].value=False
  self.assertEqual(namespace['control_answer'](control),['lab'])
 def test_count_fields_start_blank_and_reject_invalid_numbers(self):
  namespace={}
  with contextlib.redirect_stdout(io.StringIO()):exec(later.setup_code(later.UNITS[-1]).replace('await piplite.install','piplite.install'),namespace)
  control=namespace['controls']['missing'];collect=namespace['control_answer']
  self.assertEqual(control.value,'');self.assertIsNone(collect(control))
  for invalid in ['-1','1.5','text','NaN']:
   control.value=invalid;self.assertIsNone(collect(control))
  for value in ['0','12']:
   control.value=value;self.assertEqual(collect(control),int(value))
if __name__=='__main__':unittest.main()
