"""Behavioral and parsing checks for the revised extraction definition."""
import json
import tempfile
import unittest
from pathlib import Path
from extract import LocalLLM, ROOT, extract_candidates, normalize, source_passages, verify_candidates


class ParsingTests(unittest.TestCase):
    def test_hidden_metadata_is_not_product_text(self):
        html = '<ix:header><ix:hidden>Fake launch HiddenBond</ix:hidden></ix:header><p>Today we launched Atlas Sensor.</p><div style="display: none">Secret product.</div>'
        text = ' '.join(source_passages(html).values())
        self.assertIn('Atlas Sensor', text)
        self.assertNotIn('HiddenBond', text)
        self.assertNotIn('Secret', text)

    def test_trademark_typography_does_not_break_name_grounding(self):
        self.assertEqual(normalize('NVIDIA Spectrum™-6'), normalize('NVIDIA Spectrum-6'))


def model_check():
    passages = {
        'P0000': 'During the quarter, Example Corp introduced Atlas Sensor, a wireless temperature sensor.',
        'P0001': 'Sales of the existing Navigator Router rose 12%. No new Navigator version was introduced.',
        'P0002': 'Example Corp issued 0.500% Notes due 2031 and appointed Jane Smith as CEO.',
        'P0003': 'The company announced a partnership with Beta Cloud using the existing Navigator Router.',
        'P0004': 'Example Corp unveiled Quantum Router 2, a new network router that will be available next quarter.'}
    llm = LocalLLM('qwen3:14b', ROOT / 'cache' / 'tests')
    result = extract_candidates(llm, 'Example Corp', passages)
    supported = []
    for product in result['products']:
        evidence = ' '.join(passages[i] for i in product['source_ids'])
        assert normalize(product['name']) in normalize(evidence)
        supported.append({'id': len(supported), **product, 'evidence': evidence})
    decisions = verify_candidates(llm, supported)
    names = {p['name'] for p in supported if decisions[p['id']]['accept']}
    assert names == {'Atlas Sensor', 'Quantum Router 2'}, (names, result, decisions)
    output = {'synthetic_test': 'passed', 'accepted_names': sorted(names),
              'cases': ['reporting-quarter launch accepted', 'named future-availability unveiling accepted',
                        'existing sales mention rejected', 'financing/appointment rejected', 'partnership-only rejected'],
              'raw_extraction': result, 'verification': decisions}
    (ROOT / 'test_results.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
    print('Five synthetic classification scenarios passed; these are not an accuracy benchmark.')


if __name__ == '__main__':
    unittest.main(exit=False)
    model_check()
