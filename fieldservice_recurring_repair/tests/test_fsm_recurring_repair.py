# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class FSMRecurringRepairCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Equipment = cls.env["fsm.equipment"]
        cls.Recurring = cls.env["fsm.recurring"]
        # disable tracking in test
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.test_equipment = cls.Equipment.create({"name": "Equipment"})
        cls.test_equipment2 = cls.Equipment.create({"name": "Equipment 2"})
        cls.Frequency = cls.env["fsm.frequency"]
        cls.FrequencySet = cls.env["fsm.frequency.set"]

        cls.rule = cls.Frequency.create(
            {
                "name": "All weekdays",
                "interval_type": "monthly",
                "use_byweekday": True,
                "mo": True,
                "tu": True,
                "we": True,
                "th": True,
                "fr": True,
            }
        )
        cls.fr_set = cls.FrequencySet.create(
            {
                "name": "31th only",
                "schedule_days": 365,
                "fsm_frequency_ids": [(6, 0, cls.rule.ids)],
            }
        )
        cls.fsm_order_type = cls.env["fsm.order.type"].create(
            {
                "name": "Install",
                "internal_type": "fsm",
            }
        )
        cls.fsm_order_template_install = cls.env["fsm.template"].create(
            {
                "name": "Install",
                "duration": 1,
                "type_id": cls.fsm_order_type.id,
            }
        )
        cls.fsm_recurring_template_install = cls.env["fsm.recurring.template"].create(
            {
                "name": "Test Install",
                "max_orders": 4,
                "fsm_order_template_id": cls.fsm_order_template_install.id,
                "fsm_frequency_set_id": cls.fr_set.id,
                "company_id": cls.env.ref("base.main_company").id,
            }
        )

        cls.fsm_order_template_maintenance = cls.env["fsm.template"].create(
            {
                "name": "Maintenance",
                "duration": 2,
                "type_id": cls.env.ref("fieldservice_repair.fsm_order_type_repair").id,
            }
        )
        cls.fsm_recurring_template_daily = cls.env["fsm.recurring.template"].create(
            {
                "name": "Test Maintenance",
                "max_orders": 4,
                "fsm_order_template_id": cls.fsm_order_template_maintenance.id,
                "fsm_frequency_set_id": cls.fr_set.id,
                "company_id": cls.env.ref("base.main_company").id,
            }
        )
        cls.test_loc_partner = cls.env["res.partner"].create(
            {"name": "Test Loc Partner", "phone": "ABC", "email": "tlp@email.com"}
        )
        cls.test_location = cls.env["fsm.location"].create(
            {
                "name": "Test Location",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": cls.test_loc_partner.id,
                "customer_id": cls.test_loc_partner.id,
                "owner_id": cls.test_loc_partner.id,
            }
        )

    def _check_fsm_order_type(self, order, order_type):
        self.assertEqual(order.fsm_order_type_id, order_type)
        self.assertEqual(order.internal_type, order_type.internal_type)

    def test_01_fsm_order_install_multi_equip(self):
        # Create Recurring Order
        install_recurring_multi_equip = self.Recurring.create(
            {
                "fsm_recurring_template_id": self.fsm_recurring_template_install.id,
                "location_id": self.test_location.id,
                "company_id": self.env.ref("base.main_company").id,
                "equipment_ids": [
                    (6, 0, [self.test_equipment.id, self.test_equipment2.id])
                ],
            }
        )
        install_recurring_multi_equip.onchange_recurring_template_id()
        install_recurring_multi_equip.action_start()

        # Check if the orders are created
        self.assertEqual(install_recurring_multi_equip.state, "progress")
        self.assertEqual(len(install_recurring_multi_equip.fsm_order_ids), 4)

    def test_02_fsm_order_install_single_equip(self):
        install_recurring_single_equip = self.Recurring.create(
            {
                "fsm_recurring_template_id": self.fsm_recurring_template_install.id,
                "location_id": self.test_location.id,
                "company_id": self.env.ref("base.main_company").id,
                "equipment_ids": [(6, 0, [self.test_equipment.id])],
            }
        )
        install_recurring_single_equip.onchange_recurring_template_id()
        install_recurring_single_equip.action_start()

        # Check if the orders are created
        self.assertEqual(install_recurring_single_equip.state, "progress")
        self.assertEqual(len(install_recurring_single_equip.fsm_order_ids), 4)

    def test_03_fsm_order_repair_multi_equip(self):
        # Create Recurring Order
        repair_recurring_multi_equip = self.Recurring.create(
            {
                "fsm_recurring_template_id": self.fsm_recurring_template_daily.id,
                "location_id": self.test_location.id,
                "company_id": self.env.ref("base.main_company").id,
                "equipment_ids": [
                    (6, 0, [self.test_equipment.id, self.test_equipment2.id])
                ],
            }
        )
        repair_recurring_multi_equip.onchange_recurring_template_id()
        repair_recurring_multi_equip.action_start()

        # Check if the orders are created
        self.assertEqual(repair_recurring_multi_equip.state, "progress")
        self.assertEqual(len(repair_recurring_multi_equip.fsm_order_ids), 8)

    def test_04_fsm_order_repair_single_equip(self):
        repair_recurring_single_equip = self.Recurring.create(
            {
                "fsm_recurring_template_id": self.fsm_recurring_template_daily.id,
                "location_id": self.test_location.id,
                "equipment_ids": [(6, 0, [self.test_equipment.id])],
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        repair_recurring_single_equip.onchange_recurring_template_id()
        repair_recurring_single_equip.action_start()

        # Check if the orders are created
        self.assertEqual(repair_recurring_single_equip.state, "progress")
        self.assertEqual(len(repair_recurring_single_equip.fsm_order_ids), 4)
