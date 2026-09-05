import unittest
from tools.check_public_data import check_text

class PublicDataTests(unittest.TestCase):
    def test_private_identifiers_blocked(self):
        for value in ['192.168.9.10','10.0.0.1','aa:bb:cc:dd:ee:ff','Bearer '+'x'*24]:
            with self.assertRaises(ValueError):check_text(value)
    def test_public_model_ids_and_versions(self):
        check_text('xiaomi.vacuum.ov42gl; 2026.9.0; 1.0.0; https://example.org/manual')
