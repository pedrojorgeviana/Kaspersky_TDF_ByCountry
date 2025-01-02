import unittest
import os
import json
from filter_country import filter_by_country

class TestFilterByCountry(unittest.TestCase):

    def setUp(self):
        # Create the feeds folder
        self.folder = './feeds'
        os.makedirs(self.folder, exist_ok=True)

        # Create files within feeds
        self.test_file = os.path.join(self.folder, 'IP_Reputation_test.json')
        self.filtered_file = os.path.join(self.folder, 'test_filtered_feed.json')
        self.test_data = [
            {"ip_whois": {"country": "ES"}},
            {"ip_whois": {"country": "US"}},
            {"ip_whois": {"country": "ES"}},
            {"ip_whois": {"country": "FR"}}
        ]
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f, ensure_ascii=False, indent=4)

    def tearDown(self):
        # Remove files generated during tests
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.filtered_file):
            os.remove(self.filtered_file)

    def test_filter_by_country_es(self):
        filter_by_country(self.test_file, self.filtered_file)
        with open(self.filtered_file, 'r', encoding='utf-8') as f:
            filtered_data = json.load(f)
        for record in filtered_data:
            self.assertEqual(record["ip_whois"]["country"], "ES")
        self.assertEqual(len(filtered_data), 2)

    def test_filter_by_country_no_data(self):
        no_match_file = os.path.join(self.folder, 'no_match.json')
        test_data = [{"ip_whois": {"country": "US"}}, {"ip_whois": {"country": "FR"}}]
        with open(no_match_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=4)
        filter_by_country(no_match_file, self.filtered_file)
        with open(self.filtered_file, 'r', encoding='utf-8') as f:
            filtered_data = json.load(f)
        self.assertEqual(len(filtered_data), 0)
        os.remove(no_match_file)

    def test_filter_by_country_empty_file(self):
        empty_file = os.path.join(self.folder, 'empty.json')
        with open(empty_file, 'w', encoding='utf-8') as f:
            f.write("[]")
        filter_by_country(empty_file, self.filtered_file)
        with open(self.filtered_file, 'r', encoding='utf-8') as f:
            filtered_data = json.load(f)
        self.assertEqual(len(filtered_data), 0)
        os.remove(empty_file)

    def test_filter_by_country_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            filter_by_country(os.path.join(self.folder, 'nonexistent_file.json'), self.filtered_file)

    def test_filter_by_country_invalid_json(self):
        invalid_file = os.path.join(self.folder, 'invalid.json')
        with open(invalid_file, 'w', encoding='utf-8') as f:
            f.write("{ invalid json }")
        with self.assertRaises(json.JSONDecodeError):
            filter_by_country(invalid_file, self.filtered_file)
        os.remove(invalid_file)

if __name__ == '__main__':
    unittest.main()
