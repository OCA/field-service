from odoo.addons.fieldservice.tests.test_fsm_common import FSMCommon


class TestFieldserviceCrm(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

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

    def test_action_create_fsm_order(self):
        lead = self.env["crm.lead"].create(
            {
                "name": "Test Opportunity",
                "type": "opportunity",
                "fsm_location_id": self.location_2.id,
                "description": "<p>Test description</p>",
                "priority": "1",
            }
        )
        action = lead.action_create_fsm_order()
        ctx = action.get("context", {})
        self.assertEqual(ctx.get("default_opportunity_id"), lead.id)
        self.assertEqual(ctx.get("default_location_id"), self.location_2.id)
        self.assertEqual(ctx.get("default_description"), "<p>Test description</p>")
        self.assertEqual(ctx.get("default_priority"), "1")
