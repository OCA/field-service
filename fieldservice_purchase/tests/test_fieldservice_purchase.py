# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestFieldservicePurchase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestFieldservicePurchase, cls).setUpClass()
        cls.Pricelist = cls.env["product.supplierinfo"]
        Partner = cls.env["res.partner"]
        FSMPerson = cls.env["fsm.person"]
        cls.vendor = Partner.create({"name": "vendor test"})
        cls.worker = FSMPerson.create(
            {"name": "worker test", "partner_id": cls.vendor.id}
        )

    def test_pricelist_count(self):
        Pricelist = self.Pricelist
        vendor = self.vendor
        worker = self.worker
        self.assertEqual(worker.pricelist_count, 0)
        Pricelist.create({"name": vendor.id})
        worker.invalidate_cache()
        self.assertEqual(worker.pricelist_count, 1)

    def test_action_view_pricelists(self):
        Pricelist = self.Pricelist
        worker = self.worker
        vendor = self.vendor
        action_domain = worker.action_view_pricelists().get("domain")
        res_id = worker.action_view_pricelists().get("res_id")
        self.assertIsNotNone(action_domain)
        self.assertFalse(res_id)
        pricelist = Pricelist.create({"name": vendor.id})
        action_domain = worker.action_view_pricelists().get("domain")
        self.assertFalse(action_domain)
        res_id = worker.action_view_pricelists().get("res_id")
        self.assertEqual(res_id, pricelist.id)
