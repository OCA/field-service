# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged

from .test_subcontracting_common import SubcontractingCommon


@tagged("post_install", "-at_install")
class TestSubcontractPOCreation(SubcontractingCommon):
    """Test automatic Purchase Order creation for subcontracted FSOs."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_subcontracting_data(
            vendor_name="Test Vendor Co.",
            worker_name="External Vendor Worker",
            order_type_name="Test Service Type",
            template_name="Test Service Template",
        )
        cls.non_vendor_partner = cls.env["res.partner"].create(
            {
                "name": "Test Non-Vendor",
                "supplier_rank": 0,
            }
        )
        cls.order_type_no_product = cls.env["fsm.order.type"].create(
            {
                "name": "Test Type No Product",
            }
        )
        cls.template_no_product = cls.env["fsm.template"].create(
            {
                "name": "Test Template No Product",
                "type_id": cls.order_type_no_product.id,
            }
        )
        cls.product_without_supplierinfo = cls.env["product.product"].create(
            {
                "name": "Subcontracted Service Without Supplierinfo",
                "type": "service",
                "purchase_method": "receive",
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
            }
        )
        cls.template_without_supplierinfo = cls.env["fsm.template"].create(
            {
                "name": "Test Template Without Supplierinfo",
                "type_id": cls.order_type.id,
                "subcontract_product_id": cls.product_without_supplierinfo.id,
            }
        )
        cls.product_invalid_configuration = cls.env["product.product"].create(
            {
                "name": "Invalid Subcontracted Product",
                "type": "service",
                "purchase_method": "purchase",
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
            }
        )
        cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.vendor_partner.id,
                "product_tmpl_id": cls.product_invalid_configuration.product_tmpl_id.id,
                "price": 100.0,
            }
        )
        cls.template_invalid_product_configuration = cls.env["fsm.template"].create(
            {
                "name": "Test Template Invalid Product Configuration",
                "type_id": cls.order_type.id,
                "subcontract_product_id": cls.product_invalid_configuration.id,
            }
        )
        cls.internal_worker = cls._create_worker(
            "Internal Worker",
            is_fsm_subcontractor=False,
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test Analytic",
                "plan_id": cls.env.ref("analytic.analytic_plan_projects").id,
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
                "account_id": cls.analytic_account.id,
            }
        )
        cls.fsm_purchase_user = cls._create_subcontracting_user(
            "subcontracting_fsm_purchase_po",
            "fieldservice.group_fsm_dispatcher",
            "purchase.group_purchase_user",
        )
        cls.fsm_only_user = cls._create_subcontracting_user(
            "subcontracting_fsm_only_po",
            "fieldservice.group_fsm_dispatcher",
        )
        cls.assigned_stage = cls._create_stage_with_action(
            "Assigned Subcontracting Test",
            "fieldservice_subcontracting.action_create_subcontract_po",
            sequence=20,
        )

    def test_subcontractor_constraint_vendor(self):
        """Marking a non-vendor partner as subcontractor should fail."""
        with self.assertRaises(ValidationError):
            self.env["fsm.person"].create(
                {
                    "name": "Bad Worker",
                    "partner_id": self.non_vendor_partner.id,
                    "is_fsm_subcontractor": True,
                }
            )

    def test_create_po_for_subcontractor(self):
        """PO should be created when _create_subcontract_po is called."""
        scheduled_start = datetime(2026, 1, 15, 8, 0, 0)
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
            project=self.project,
        )
        fso.write(
            {
                "scheduled_date_start": scheduled_start,
                "scheduled_duration": 1.0,
            }
        )
        self.assertFalse(fso.purchase_order_ids)
        fso._create_subcontract_po()
        self.assertTrue(fso.purchase_order_ids)
        po = fso.purchase_order_ids
        self.assertEqual(po.partner_id, self.vendor_partner)
        self.assertEqual(po.fsm_order_id, fso)
        self.assertEqual(po.state, "draft")
        self.assertEqual(po.origin, fso.name)
        self.assertEqual(len(po.order_line), 1)
        line = po.order_line[0]
        self.assertEqual(line.product_id, self.service_product)
        self.assertEqual(line.product_qty, 1.0)
        self.assertEqual(po.date_planned, fso.scheduled_date_end)
        self.assertEqual(line.date_planned, fso.scheduled_date_end)
        expected_dist = {str(self.analytic_account.id): 100.0}
        self.assertEqual(line.analytic_distribution, expected_dist)

    def test_assigned_stage_creates_po_for_configured_subcontractor(self):
        """Assigned stage should create PO through the configured server action."""
        scheduled_start = datetime(2026, 1, 15, 8, 0, 0)
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
            project=self.project,
        )
        fso.write(
            {
                "scheduled_date_start": scheduled_start,
                "scheduled_duration": 2.0,
            }
        )

        fso.with_user(self.fsm_purchase_user).write(
            {"stage_id": self.assigned_stage.id}
        )

        fso.invalidate_recordset(["purchase_order_ids"])
        po = fso.purchase_order_ids
        self.assertEqual(len(po), 1)
        self.assertEqual(po.create_uid, self.fsm_purchase_user)
        self.assertEqual(po.partner_id, self.vendor_partner)
        self.assertEqual(po.fsm_order_id, fso)
        self.assertEqual(po.state, "draft")
        self.assertEqual(po.origin, fso.name)
        self.assertEqual(po.date_planned, fso.scheduled_date_end)
        self.assertEqual(len(po.order_line), 1)
        line = po.order_line
        self.assertEqual(line.product_id, self.service_product)
        self.assertEqual(line.product_qty, 2.0)
        self.assertEqual(line.qty_received, 0.0)
        self.assertEqual(line.date_planned, fso.scheduled_date_end)
        self.assertEqual(
            line.analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )
        self.assertTrue(
            any(
                "Subcontract Purchase Order:" in message.body
                for message in fso.message_ids
            )
        )

    def test_assigned_stage_does_not_create_po_without_subcontract_product(self):
        """Assigned stage should not create PO when template lacks product."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type_no_product,
            template=self.template_no_product,
        )

        fso.write({"stage_id": self.assigned_stage.id})

        self.assertFalse(fso.purchase_order_ids)
        self.assertTrue(
            any(
                "The outsourcing product is not configured" in message.body
                for message in fso.message_ids
            )
        )

    def test_assigned_stage_does_not_create_po_without_supplierinfo(self):
        """Assigned stage should require a vendor price for the worker vendor."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template_without_supplierinfo,
        )

        fso.write({"stage_id": self.assigned_stage.id})

        self.assertFalse(fso.purchase_order_ids)
        self.assertTrue(
            any(
                "has no vendor price configured" in message.body
                for message in fso.message_ids
            )
        )

    def test_assigned_stage_does_not_create_po_with_invalid_product_setup(self):
        """Assigned stage should validate RF-03 product settings."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template_invalid_product_configuration,
        )

        fso.write({"stage_id": self.assigned_stage.id})

        self.assertFalse(fso.purchase_order_ids)
        self.assertTrue(
            any(
                "must bill based on received quantities" in message.body
                for message in fso.message_ids
            )
        )

    def test_assigned_stage_does_not_create_po_for_internal_worker(self):
        """Assigned stage should not create PO when worker is not subcontractor."""
        fso = self._create_fso(
            worker=self.internal_worker,
            order_type=self.order_type,
            template=self.template,
        )

        fso.write({"stage_id": self.assigned_stage.id})

        self.assertFalse(fso.purchase_order_ids)
        self.assertTrue(
            any("is an internal worker" in message.body for message in fso.message_ids)
        )

    def test_create_po_with_fsm_and_purchase_user(self):
        """PO creation action requires FSM and Purchase permissions."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )

        fso.with_user(self.fsm_purchase_user)._create_subcontract_po()

        self.assertTrue(fso.purchase_order_ids)
        self.assertEqual(fso.purchase_order_ids.create_uid, self.fsm_purchase_user)

    def test_create_po_without_purchase_user_is_blocked(self):
        """FSM users without Purchase rights cannot create subcontract POs."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )

        with self.assertRaises(AccessError):
            fso.with_user(self.fsm_only_user)._create_subcontract_po()
        self.assertFalse(fso.purchase_order_ids)

    def test_po_date_planned_updates_when_fso_schedule_changes(self):
        """Changing FSO schedule should update active subcontract POs."""
        scheduled_start = datetime(2026, 1, 15, 8, 0, 0)
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
            project=self.project,
        )
        fso.write(
            {
                "scheduled_date_start": scheduled_start,
                "scheduled_duration": 3.0,
            }
        )
        fso._create_subcontract_po()
        po = fso.purchase_order_ids

        new_scheduled_start = scheduled_start + timedelta(days=1)
        fso.write(
            {
                "scheduled_date_start": new_scheduled_start,
                "scheduled_duration": 3.0,
            }
        )

        expected_date = new_scheduled_start + timedelta(hours=3)
        po.invalidate_recordset(["date_planned"])
        po.order_line.invalidate_recordset(["date_planned"])
        self.assertEqual(fso.scheduled_date_end, expected_date)
        self.assertEqual(po.date_planned, expected_date)
        self.assertEqual(po.order_line.date_planned, expected_date)

    def test_po_date_planned_updates_with_fsm_and_purchase_user(self):
        """FSM and Purchase user can update FSO schedule and linked PO dates."""
        scheduled_start = datetime(2026, 1, 15, 8, 0, 0)
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )
        fso.write(
            {
                "scheduled_date_start": scheduled_start,
                "scheduled_duration": 1.0,
            }
        )
        fso._create_subcontract_po()
        po = fso.purchase_order_ids

        new_scheduled_start = scheduled_start + timedelta(days=2)
        fso.with_user(self.fsm_purchase_user).write(
            {
                "scheduled_date_start": new_scheduled_start,
                "scheduled_duration": 2.0,
            }
        )

        expected_date = new_scheduled_start + timedelta(hours=2)
        po.invalidate_recordset(["date_planned"])
        po.order_line.invalidate_recordset(["date_planned"])
        self.assertEqual(po.date_planned, expected_date)
        self.assertEqual(po.order_line.date_planned, expected_date)

    def test_no_po_for_internal_worker(self):
        """No PO should be created for internal (non-subcontractor) workers."""
        fso = self._create_fso(
            worker=self.internal_worker,
            order_type=self.order_type,
            template=self.template,
        )
        fso._create_subcontract_po()
        self.assertFalse(fso.purchase_order_ids)
        self.assertTrue(
            any("is an internal worker" in message.body for message in fso.message_ids)
        )

    def test_no_duplicate_po(self):
        """Calling _create_subcontract_po twice should not create a second PO."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )
        fso._create_subcontract_po()
        po1 = fso.purchase_order_ids
        fso._create_subcontract_po()
        self.assertEqual(fso.purchase_order_ids, po1)
        self.assertEqual(len(fso.purchase_order_ids), 1)

    def test_new_po_after_previous_po_cancelled(self):
        """A new PO can be created after the previous PO was cancelled."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )
        fso._create_subcontract_po()
        po1 = fso.purchase_order_ids
        po1.button_cancel()

        fso._create_subcontract_po()
        self.assertEqual(len(fso.purchase_order_ids), 2)
        self.assertEqual(len(fso._get_active_subcontract_purchase_orders()), 1)

    def test_no_po_without_product(self):
        """No PO if the order type has no subcontracting product."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type_no_product,
            template=self.template_no_product,
        )
        fso._create_subcontract_po()
        self.assertFalse(fso.purchase_order_ids)

    def test_no_po_without_assigned_worker(self):
        """No PO if the FSO has no assigned worker."""
        fso = self._create_fso(
            order_type=self.order_type,
            template=self.template,
        )

        fso._create_subcontract_po()

        self.assertFalse(fso.purchase_order_ids)
        self.assertTrue(
            any(
                "It does not have an assigned worker." in message.body
                for message in fso.message_ids
            )
        )

    def test_no_po_when_subcontractor_partner_is_not_supplier(self):
        """No PO if subcontractor data becomes inconsistent."""
        self.vendor_partner.supplier_rank = 0
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )

        fso._create_subcontract_po()

        self.assertFalse(fso.purchase_order_ids)
        self.assertTrue(
            any(
                "not associated as a supplier" in message.body
                for message in fso.message_ids
            )
        )

    def test_smart_button_count(self):
        """Purchase order count should reflect PO existence."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )
        self.assertEqual(fso.purchase_order_count, 0)
        fso._create_subcontract_po()
        self.assertEqual(fso.purchase_order_count, 1)

    def test_action_view_purchase_order(self):
        """Purchase Order smart button should open linked POs."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )
        fso._create_subcontract_po()
        purchase_order = fso.purchase_order_ids

        action = fso.action_view_purchase_order()

        self.assertEqual(action["res_model"], "purchase.order")
        self.assertEqual(action["res_id"], purchase_order.id)
        self.assertEqual(action["view_mode"], "form")

        purchase_order.button_cancel()
        fso._create_subcontract_po()
        action = fso.action_view_purchase_order()

        self.assertEqual(action["view_mode"], "list,form")
        self.assertEqual(action["domain"], [("id", "in", fso.purchase_order_ids.ids)])
        self.assertNotIn("res_id", action)

    def test_action_view_fsm_order_from_purchase_order(self):
        """Purchase Order smart button should open the linked FSO."""
        unlinked_purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor_partner.id,
            }
        )
        self.assertEqual(unlinked_purchase_order.fsm_order_count, 0)

        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )
        fso._create_subcontract_po()
        purchase_order = fso.purchase_order_ids

        action = purchase_order.action_view_fsm_order()

        self.assertEqual(purchase_order.fsm_order_count, 1)
        self.assertEqual(action["res_model"], "fsm.order")
        self.assertEqual(action["res_id"], fso.id)
        self.assertEqual(action["view_mode"], "form")


@tagged("post_install", "-at_install")
class TestSubcontractPOClose(SubcontractingCommon):
    """Test PO delivered quantity update when FSO is closed."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_subcontracting_data()
        cls.order_type_no_product = cls.env["fsm.order.type"].create(
            {
                "name": "Test Type No Product",
            }
        )
        cls.template_no_product = cls.env["fsm.template"].create(
            {
                "name": "Test Template No Product",
                "type_id": cls.order_type_no_product.id,
            }
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
            }
        )
        cls.fsm_purchase_user = cls._create_subcontracting_user(
            "subcontracting_fsm_purchase_close",
            "fieldservice.group_fsm_dispatcher",
            "purchase.group_purchase_user",
        )
        cls.done_stage = cls._create_stage_with_action(
            "Done Subcontracting Test",
            "fieldservice_subcontracting.action_update_subcontract_po_qty",
            sequence=81,
            is_closed=True,
        )

    def test_update_po_qty_on_close(self):
        """Closing the FSO should update PO line qty_received."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
            project=self.project,
        )
        fso._create_subcontract_po()
        po = fso.purchase_order_ids
        self.assertTrue(po)

        self.env["account.analytic.line"].create(
            {
                "name": "Work done - day 1",
                "project_id": self.project.id,
                "fsm_order_id": fso.id,
                "employee_id": self.employee.id,
                "unit_amount": 4.0,
            }
        )
        self.env["account.analytic.line"].create(
            {
                "name": "Work done - day 2",
                "project_id": self.project.id,
                "fsm_order_id": fso.id,
                "employee_id": self.employee.id,
                "unit_amount": 3.5,
            }
        )

        fso._update_subcontract_po_qty()

        po_line = po.order_line[0]
        po_line.invalidate_recordset(["product_qty", "qty_received"])
        self.assertAlmostEqual(po_line.product_qty, 1.0)
        self.assertAlmostEqual(po_line.qty_received, 7.5)

    def test_done_stage_updates_delivered_qty_from_timesheets(self):
        """Done stage should update delivered qty through the server action."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
            project=self.project,
        )
        fso._create_subcontract_po()
        po_line = fso.purchase_order_ids.order_line
        self.env["account.analytic.line"].create(
            {
                "name": "Work done - stage action 1",
                "project_id": self.project.id,
                "fsm_order_id": fso.id,
                "employee_id": self.employee.id,
                "unit_amount": 1.5,
            }
        )
        self.env["account.analytic.line"].create(
            {
                "name": "Work done - stage action 2",
                "project_id": self.project.id,
                "fsm_order_id": fso.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.0,
            }
        )

        fso.with_user(self.fsm_purchase_user).write({"stage_id": self.done_stage.id})

        po_line.invalidate_recordset(["product_qty", "qty_received"])
        self.assertAlmostEqual(po_line.product_qty, 1.0)
        self.assertAlmostEqual(po_line.qty_received, 3.5)
        self.assertTrue(
            any(
                "Delivered quantity updated to 3.50 hours" in message.body
                for message in fso.purchase_order_ids.message_ids
            )
        )

    def test_update_po_qty_with_fsm_and_purchase_user(self):
        """FSM and Purchase user can update PO delivered quantity."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
            project=self.project,
        )
        fso._create_subcontract_po()
        po = fso.purchase_order_ids
        self.env["account.analytic.line"].create(
            {
                "name": "Work done",
                "project_id": self.project.id,
                "fsm_order_id": fso.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.25,
            }
        )

        fso.with_user(self.fsm_purchase_user)._update_subcontract_po_qty()

        po_line = po.order_line[0]
        po_line.invalidate_recordset(["product_qty", "qty_received"])
        self.assertAlmostEqual(po_line.product_qty, 1.0)
        self.assertAlmostEqual(po_line.qty_received, 2.25)

    def test_no_update_without_subcontract_product(self):
        """PO quantity should not update when FSO has no subcontract product."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
            project=self.project,
        )
        fso._create_subcontract_po()
        po_line = fso.purchase_order_ids.order_line
        self.env["account.analytic.line"].create(
            {
                "name": "Work done",
                "project_id": self.project.id,
                "fsm_order_id": fso.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.0,
            }
        )
        fso.write(
            {
                "type": self.order_type_no_product.id,
                "template_id": self.template_no_product.id,
            }
        )

        fso._update_subcontract_po_qty()

        self.assertAlmostEqual(po_line.product_qty, 1.0)
        self.assertAlmostEqual(po_line.qty_received, 0.0)

    def test_no_update_without_po(self):
        """Should not fail if FSO has no PO linked."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )

        fso._update_subcontract_po_qty()
