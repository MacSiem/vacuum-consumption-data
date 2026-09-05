import unittest

from tools.report_inventory import report


class InventoryReportTests(unittest.TestCase):
    def test_every_miot_protocol_id_has_a_nonpass_disposition(self):
        inventory = report()
        self.assertEqual(inventory["protocol_id_denominator"], 356)
        self.assertEqual(len(inventory["records"]), 356)
        self.assertTrue(all(row["disposition"] != "goalPASS" for row in inventory["records"]))
        self.assertTrue(all(row["source_sha256"] for row in inventory["records"]))
