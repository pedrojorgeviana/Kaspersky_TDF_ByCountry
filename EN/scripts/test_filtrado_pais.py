import unittest
import os
import json
from ES.scripts.filtrado_pais import filtrar_por_pais

class TestFiltradoPais(unittest.TestCase):

    def setUp(self):
        # Crear carpeta feeds
        self.carpeta = 'feeds'
        os.makedirs(self.carpeta, exist_ok=True)

        # Crear archivos dentro de feeds
        self.test_file = os.path.join(self.carpeta, 'IP_Reputation_test.json')
        self.filtered_file = os.path.join(self.carpeta, 'test_filtered_feed.json')
        self.test_data = [
            {"ip_whois": {"country": "ES"}},
            {"ip_whois": {"country": "US"}},
            {"ip_whois": {"country": "ES"}},
            {"ip_whois": {"country": "FR"}}
        ]
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f, ensure_ascii=False, indent=4)

    def tearDown(self):
        # Eliminar archivos generados en las pruebas
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.filtered_file):
            os.remove(self.filtered_file)

    def test_filtrar_por_pais_es(self):
        filtrar_por_pais(self.test_file, self.filtered_file)
        with open(self.filtered_file, 'r', encoding='utf-8') as f:
            filtered_data = json.load(f)
        for registro in filtered_data:
            self.assertEqual(registro["ip_whois"]["country"], "ES")
        self.assertEqual(len(filtered_data), 2)

    def test_filtrar_por_pais_no_data(self):
        no_match_file = os.path.join(self.carpeta, 'no_match.json')
        test_data = [{"ip_whois": {"country": "US"}}, {"ip_whois": {"country": "FR"}}]
        with open(no_match_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=4)
        filtrar_por_pais(no_match_file, self.filtered_file)
        with open(self.filtered_file, 'r', encoding='utf-8') as f:
            filtered_data = json.load(f)
        self.assertEqual(len(filtered_data), 0)
        os.remove(no_match_file)

    def test_filtrar_por_pais_empty_file(self):
        empty_file = os.path.join(self.carpeta, 'empty.json')
        with open(empty_file, 'w', encoding='utf-8') as f:
            f.write("[]")
        filtrar_por_pais(empty_file, self.filtered_file)
        with open(self.filtered_file, 'r', encoding='utf-8') as f:
            filtered_data = json.load(f)
        self.assertEqual(len(filtered_data), 0)
        os.remove(empty_file)

    def test_filtrar_por_pais_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            filtrar_por_pais(os.path.join(self.carpeta, 'archivo_inexistente.json'), self.filtered_file)

    def test_filtrar_por_pais_invalid_json(self):
        invalid_file = os.path.join(self.carpeta, 'invalid.json')
        with open(invalid_file, 'w', encoding='utf-8') as f:
            f.write("{ invalid json }")
        with self.assertRaises(json.JSONDecodeError):
            filtrar_por_pais(invalid_file, self.filtered_file)
        os.remove(invalid_file)

if __name__ == '__main__':
    unittest.main()
