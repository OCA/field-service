from odoo.tests import common


class TestFieldserviceCrm(common.TransactionCase):
    def test_fieldservicecrm(self):
        location_1 = self.env["fsm.location"].create(
            {
                "name": "Summer's House",
                "owner_id": self.env["res.partner"]
                .create({"name": "Summer's Parents"})
                .id,
            }
        )
        crm_1 = self.env["crm.lead"].create(
            {
                "name": "Test CRM",
                "fsm_location_id": location_1.id,
            }
        )
        self.env["fsm.order"].create(
            {
                "location_id": location_1.id,
                "opportunity_id": crm_1.id,
            }
        )
        crm_1._compute_fsm_order_count()
        self.assertEqual(crm_1.fsm_order_count, 1)

        location_1._compute_opportunity_count()
        self.assertEqual(location_1.opportunity_count, 1)

    def test_action_create_fsm_order(self):
        location = self.env["fsm.location"].create(
            {
                "name": "Test Location",
                "owner_id": self.env["res.partner"].create({"name": "Test Owner"}).id,
            }
        )
        lead = self.env["crm.lead"].create(
            {
                "name": "Test Opportunity",
                "type": "opportunity",
                "fsm_location_id": location.id,
                "description": "<p>Test description</p>",
                "priority": "1",
            }
        )
        action = lead.action_create_fsm_order()
        ctx = action.get("context", {})
        self.assertEqual(ctx.get("default_opportunity_id"), lead.id)
        self.assertEqual(ctx.get("default_location_id"), location.id)
        self.assertEqual(ctx.get("default_description"), "<p>Test description</p>")
        self.assertEqual(ctx.get("default_priority"), "1")
