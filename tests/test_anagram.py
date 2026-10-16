import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from Anagrams.anagram import find_anagrams, tile_indices, normalize_rack, anagrams
from Anagrams.main import plan_word


class SolverTests(unittest.TestCase):
    def test_no_duplicate_results_and_stable_order(self):
        words=find_anagrams('LETTER')
        self.assertEqual(len(words),len(set(words)))
        self.assertEqual(words,sorted(words,key=lambda w:(-len(w),w)))

    def test_counter_limits_and_blanks(self):
        self.assertNotIn('TEE',find_anagrams('TEA'))
        self.assertIn('TEE',find_anagrams('TE?'))
        self.assertEqual(normalize_rack('a a\na b b c'),'AAABBC')

    def test_legacy_exact_helper_retains_short_words(self):
        self.assertIn('AA',anagrams('AA'))
        with self.assertRaises(ValueError):normalize_rack('ßA')

    def test_three_identical_tiles_are_distinct(self):
        self.assertEqual(tile_indices('AAABBC','ABACA'),[0,3,1,5,2])
        coords=[(i,i) for i in range(6)]
        self.assertEqual(plan_word('AAABBC','ABACA',coords),[(0,0),(3,3),(1,1),(5,5),(2,2)])
        self.assertEqual(len(coords),6)

    def test_bad_racks_or_impossible_words_fail(self):
        for rack in ['AB','AB0DEF','???ABC']:
            with self.assertRaises(ValueError):find_anagrams(rack)
        with self.assertRaises(ValueError):tile_indices('TEA','TEE')
        with self.assertRaises(ValueError):plan_word('STREAM','STEAM',[(1,1)])

    def test_cli_dictionary_path_independent_of_working_directory(self):
        script=Path(__file__).parents[1]/'Anagrams'/'main.py'
        with tempfile.TemporaryDirectory() as cwd:
            output=subprocess.check_output([sys.executable,str(script),'STREAM','--json'],cwd=cwd,text=True)
        self.assertIn('STREAM',json.loads(output))

    def test_import_does_not_load_desktop_automation(self):
        output=subprocess.check_output([sys.executable,'-c',"import sys;import Anagrams.main;assert 'pyautogui' not in sys.modules;assert 'appscript' not in sys.modules;print('safe')"],text=True)
        self.assertEqual(output.strip(),'safe')


if __name__ == '__main__':unittest.main()
