import requests

from odoo.exceptions import UserError
from odoo.tests import common


class TestFieldserviceCrm(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        cls._super_send = requests.Session.send
        super().setUpClass()
        cls.location_1 = cls.env["fsm.location"].create(
            {
                "name": "Summer's House",
                "owner_id": cls.env["res.partner"]
                .create({"name": "Summer's Parents"})
                .id,
            }
        )

        cls.fsm_user = cls.env["res.users"].create(
            {
                "name": "Fsm User",
                "login": "fsm_user",
                "groups_id": [(6, 0, [cls.env.ref("fieldservice.group_fsm_user").id])],
            }
        )

    def test_fieldservicecrm(self):
        crm_1 = self.env["crm.lead"].create(
            {
                "name": "Test CRM",
                "fsm_location_id": self.location_1.id,
            }
        )
        self.env["fsm.order"].create(
            {
                "location_id": self.location_1.id,
                "opportunity_id": crm_1.id,
            }
        )
        crm_1._compute_fsm_order_count()
        self.assertEqual(crm_1.fsm_order_count, 1)

        self.location_1._compute_opportunity_count()
        self.assertEqual(self.location_1.opportunity_count, 1)

    # Needed to avoid conflicts with fieldservice_geoengine when it's installed
    @classmethod
    def _request_handler(cls, s, r, /, **kw):
        """Don't block external requests."""
        return cls._super_send(s, r, **kw)

    def test_create_fs_order_from_lead(self):
        partner_1 = self.env["res.partner"].create(
            {
                "name": "Test partner",
                "street": "123 Test St",
                "city": "Test City",
                "zip": "12345",
                "country_id": self.env.ref("base.us").id,
            }
        )
        crm_1 = self.env["crm.lead"].create(
            {
                "name": "Test CRM",
                "partner_id": partner_1.id,
            }
        )
        crm_1.create_fsm_order()
        self.assertTrue(partner_1.fsm_location)
        self.assertEqual(partner_1.fsm_location_id, crm_1.fsm_location_id)

    def test_create_fs_order_from_lead_without_partner(self):
        crm_1 = self.env["crm.lead"].create(
            {
                "name": "Test CRM",
            }
        )
        with self.assertRaises(UserError):
            crm_1.create_fsm_order()

    def test_compute_sales_person_id_01(self):
        partner_1 = self.env["res.partner"].create(
            {
                "name": "Test partner",
                "street": "123 Test St",
                "city": "Test City",
                "zip": "12345",
                "country_id": self.env.ref("base.us").id,
            }
        )
        crm_1 = self.env["crm.lead"].create(
            {
                "name": "Test CRM",
                "partner_id": partner_1.id,
                "user_id": self.env.user.id,
            }
        )

        self.env["fsm.order"].create(
            {
                "location_id": self.location_1.id,
                "opportunity_id": crm_1.id,
            }
        )
        self.assertEqual(crm_1.user_id, crm_1.fsm_order_ids[0].sales_person_id)

    def test_compute_sales_person_id_02(self):
        fsm_order_1 = self.env["fsm.order"].create(
            {
                "name": "Test FSM Order",
                "location_id": self.location_1.id,
            }
        )

        self.assertEqual(fsm_order_1.sales_person_id, self.env.user)
