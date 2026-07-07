# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from .test_subcontracting_common import SubcontractingCommon


class TestSubcontractCancel(SubcontractingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_subcontracting_data()
        cls.fsm_purchase_user = cls._create_subcontracting_user(
            "subcontracting_fsm_purchase_cancel",
            "fieldservice.group_fsm_dispatcher",
            "purchase.group_purchase_user",
        )
        cls.assigned_stage = cls._create_stage_with_action(
            "Assigned Cancel Test",
            "fieldservice_subcontracting.action_create_subcontract_po",
            sequence=20,
        )

    def _create_fso_assigned_with_po(self):
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )
        fso.with_user(self.fsm_purchase_user).write(
            {"stage_id": self.assigned_stage.id}
        )
        fso.invalidate_recordset(["purchase_order_ids"])
        self.assertTrue(fso.purchase_order_ids)
        return fso

    def test_action_cancel_opens_wizard_when_active_po_exists(self):
        """Cancel action should ask what to do with active POs."""
        fso = self._create_fso_with_po()

        result = fso.action_cancel()

        self.assertEqual(result["res_model"], "fsm.order.cancel.confirm")
        self.assertEqual(result["context"]["default_fsm_order_id"], fso.id)
        self.assertNotEqual(
            fso.stage_id,
            self.env.ref("fieldservice.fsm_stage_cancelled"),
        )

    def test_action_cancel_blocks_multiple_orders_with_active_pos(self):
        """Multiple FSOs with active POs should be cancelled one at a time."""
        fso_1 = self._create_fso_with_po()
        fso_2 = self._create_fso_with_po()

        with self.assertRaises(UserError):
            (fso_1 | fso_2).action_cancel()

    def test_cancel_wizard_warning_without_purchase_orders(self):
        """Cancel wizard should stay quiet when there are no active POs."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )
        wizard = self.env["fsm.order.cancel.confirm"].create(
            {
                "fsm_order_id": fso.id,
            }
        )

        self.assertFalse(wizard.purchase_order_ids)
        self.assertFalse(wizard.warning_message)

    def test_cancel_wizard_warning_with_active_purchase_order(self):
        """Cancel wizard should list active POs in its warning."""
        fso = self._create_fso_with_po()
        purchase_order = fso.purchase_order_ids
        wizard = self.env["fsm.order.cancel.confirm"].create(
            {
                "fsm_order_id": fso.id,
            }
        )

        self.assertEqual(wizard.purchase_order_ids, purchase_order)
        self.assertIn(purchase_order.name, wizard.warning_message)

    def test_cancel_wizard_blocks_po_cancellation_with_posted_bill(self):
        """Posted vendor bills should block automatic PO cancellation."""
        fso = self._create_fso_with_po()
        purchase_order = fso.purchase_order_ids
        bill = self._create_posted_vendor_bill(purchase_order)
        wizard = self.env["fsm.order.cancel.confirm"].create(
            {
                "fsm_order_id": fso.id,
            }
        )

        self.assertEqual(fso._get_posted_subcontract_vendor_bills(), bill)
        self.assertIn("posted vendor bills", wizard.warning_message)
        with self.assertRaises(UserError):
            wizard.action_cancel_fsm_and_purchase_orders()
        self.assertNotEqual(purchase_order.state, "cancel")

    def test_cancel_assigned_po_with_posted_bill_is_blocked(self):
        """Posted bills should block cancelling a PO created by Assigned stage."""
        fso = self._create_fso_assigned_with_po()
        purchase_order = fso.purchase_order_ids
        bill = self._create_posted_vendor_bill(purchase_order)
        result = fso.action_cancel()
        wizard = self.env[result["res_model"]].create(
            {
                "fsm_order_id": fso.id,
            }
        )

        self.assertEqual(fso._get_posted_subcontract_vendor_bills(), bill)
        self.assertIn("posted vendor bills", wizard.warning_message)
        with self.assertRaises(UserError):
            wizard.action_cancel_fsm_and_purchase_orders()
        self.assertEqual(bill.state, "posted")
        self.assertNotEqual(purchase_order.state, "cancel")
        self.assertNotEqual(
            fso.stage_id,
            self.env.ref("fieldservice.fsm_stage_cancelled"),
        )

    def test_cancel_wizard_cancels_draft_bill_before_purchase_order(self):
        """Draft vendor bills should be cancelled before cancelling the PO."""
        fso = self._create_fso_with_po()
        purchase_order = fso.purchase_order_ids
        bill = self._create_draft_vendor_bill(purchase_order)
        wizard = self.env["fsm.order.cancel.confirm"].create(
            {
                "fsm_order_id": fso.id,
            }
        )

        wizard.action_cancel_fsm_and_purchase_orders()

        self.assertEqual(bill.state, "cancel")
        self.assertEqual(purchase_order.state, "cancel")
        self.assertEqual(fso.stage_id, self.env.ref("fieldservice.fsm_stage_cancelled"))

    def test_cancel_wizard_cancels_received_po_without_posted_bill(self):
        """Received POs without posted bills should still be cancelled."""
        fso = self._create_fso_with_po()
        purchase_order = fso.purchase_order_ids
        purchase_order.button_confirm()
        purchase_order.order_line.write({"qty_received": 2.0})
        wizard = self.env["fsm.order.cancel.confirm"].create(
            {
                "fsm_order_id": fso.id,
            }
        )

        wizard.action_cancel_fsm_and_purchase_orders()

        self.assertEqual(purchase_order.order_line.qty_received, 2.0)
        self.assertEqual(purchase_order.state, "cancel")
        self.assertEqual(fso.stage_id, self.env.ref("fieldservice.fsm_stage_cancelled"))

    def test_cancel_fso_only_keeps_purchase_order_open(self):
        """Wizard can cancel only the FSO."""
        fso = self._create_fso_with_po()
        purchase_order = fso.purchase_order_ids
        wizard = self.env["fsm.order.cancel.confirm"].create(
            {
                "fsm_order_id": fso.id,
            }
        )

        wizard.action_cancel_fsm_only()

        self.assertEqual(fso.stage_id, self.env.ref("fieldservice.fsm_stage_cancelled"))
        self.assertNotEqual(purchase_order.state, "cancel")

    def test_cancel_fso_and_purchase_orders(self):
        """Wizard can cancel the FSO and related active POs."""
        fso = self._create_fso_with_po()
        purchase_order = fso.purchase_order_ids
        wizard = self.env["fsm.order.cancel.confirm"].create(
            {
                "fsm_order_id": fso.id,
            }
        )

        wizard.action_cancel_fsm_and_purchase_orders()

        self.assertEqual(fso.stage_id, self.env.ref("fieldservice.fsm_stage_cancelled"))
        self.assertEqual(purchase_order.state, "cancel")

    def test_cancel_fso_and_purchase_orders_with_fsm_and_purchase_user(self):
        """FSM and Purchase user can cancel active POs through the wizard."""
        fso = self._create_fso_with_po()
        purchase_order = fso.purchase_order_ids
        wizard = (
            self.env["fsm.order.cancel.confirm"]
            .with_user(self.fsm_purchase_user)
            .create(
                {
                    "fsm_order_id": fso.id,
                }
            )
        )

        wizard.action_cancel_fsm_and_purchase_orders()

        self.assertEqual(fso.stage_id, self.env.ref("fieldservice.fsm_stage_cancelled"))
        self.assertEqual(purchase_order.state, "cancel")


class TestSubcontractReassignment(SubcontractingCommon):
    """Test worker reassignment protection when PO exists."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_subcontracting_data()
        cls.closed_stage = cls.env["fsm.stage"].create(
            {
                "name": "Closed Reassignment Test",
                "stage_type": "order",
                "is_closed": True,
            }
        )
        cls.internal_worker = cls._create_worker("Internal Worker")
        cls.replacement_worker = cls._create_worker("Replacement Worker")
        cls.fsm_purchase_user = cls._create_subcontracting_user(
            "subcontracting_fsm_purchase_lifecycle",
            "fieldservice.group_fsm_dispatcher",
            "purchase.group_purchase_user",
        )

    def test_reassignment_is_blocked_without_wizard(self):
        """Changing worker on FSO with PO should be blocked."""
        fso = self._create_fso_with_po()

        with self.assertRaises(UserError):
            fso.write({"person_id": self.internal_worker.id})
        self.assertEqual(fso.person_id, self.subcontractor)

    def test_reassignment_action_opens_wizard(self):
        """Reassignment action should open the confirmation wizard."""
        fso = self._create_fso_with_po()

        result = fso.action_open_reassign_confirm()
        self.assertEqual(result["res_model"], "fsm.order.reassign.confirm")
        self.assertEqual(
            result["context"]["default_fsm_order_id"],
            fso.id,
        )

    def test_reassign_worker_button_requires_created_po_and_open_stage(self):
        """Reassign Worker button should require a linked PO and open stage."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )
        self.assertFalse(fso.reassign_worker)

        fso._create_subcontract_po()
        self.assertTrue(fso.reassign_worker)

        fso._cancel_active_subcontract_purchase_orders()
        self.assertTrue(fso.purchase_order_ids)
        self.assertFalse(fso._get_active_subcontract_purchase_orders())
        self.assertTrue(fso.reassign_worker)

        fso.stage_id = self.closed_stage
        self.assertFalse(fso.reassign_worker)

    def test_reassign_worker_button_ignores_current_worker_subcontractor_flag(self):
        """Reassign Worker button should depend on linked PO and open stage."""
        fso = self._create_fso_with_po()
        purchase_order = fso.purchase_order_ids
        wizard = self.env["fsm.order.reassign.confirm"].create(
            {
                "fsm_order_id": fso.id,
                "new_person_id": self.internal_worker.id,
            }
        )
        wizard.action_confirm()

        self.assertFalse(fso.person_id.is_fsm_subcontractor)
        self.assertEqual(purchase_order.state, "cancel")
        self.assertFalse(fso._get_active_subcontract_purchase_orders())
        self.assertTrue(fso.reassign_worker)
        result = fso.action_open_reassign_confirm()
        self.assertEqual(result["res_model"], "fsm.order.reassign.confirm")

        wizard = self.env["fsm.order.reassign.confirm"].create(
            {
                "fsm_order_id": fso.id,
                "new_person_id": self.replacement_worker.id,
            }
        )
        wizard.action_confirm()
        self.assertEqual(fso.person_id, self.replacement_worker)

    def test_reassign_worker_button_stays_hidden_on_closed_stage_for_internal_worker(
        self,
    ):
        """Closed stage should hide reassignment even for internal current worker."""
        fso = self._create_fso_with_po()
        fso.with_context(skip_reassign_check=True).person_id = self.internal_worker
        fso._cancel_active_subcontract_purchase_orders()
        fso.stage_id = self.closed_stage

        self.assertFalse(fso.person_id.is_fsm_subcontractor)
        self.assertFalse(fso._get_active_subcontract_purchase_orders())
        self.assertFalse(fso.reassign_worker)

    def test_reassignment_action_without_po_is_blocked(self):
        """Reassignment action should require a subcontract PO."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )

        with self.assertRaises(UserError):
            fso.action_open_reassign_confirm()

    def test_reassignment_action_with_cancelled_po_opens_wizard(self):
        """Reassignment action should allow an FSO with only cancelled POs."""
        fso = self._create_fso_with_po()
        fso._cancel_active_subcontract_purchase_orders()

        result = fso.action_open_reassign_confirm()

        self.assertFalse(fso._get_active_subcontract_purchase_orders())
        self.assertEqual(result["res_model"], "fsm.order.reassign.confirm")
        self.assertEqual(
            result["context"]["default_fsm_order_id"],
            fso.id,
        )

    def test_reassignment_action_on_closed_stage_is_blocked(self):
        """Reassignment action should be blocked when FSO stage is closed."""
        fso = self._create_fso_with_po()
        fso.stage_id = self.closed_stage

        with self.assertRaises(UserError):
            fso.action_open_reassign_confirm()

    def test_reassign_wizard_warning_without_purchase_orders(self):
        """Reassign wizard should stay quiet when there are no active POs."""
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )
        wizard = self.env["fsm.order.reassign.confirm"].create(
            {
                "fsm_order_id": fso.id,
                "new_person_id": self.internal_worker.id,
            }
        )

        self.assertFalse(wizard.purchase_order_ids)
        self.assertFalse(wizard.warning_message)

    def test_reassign_wizard_warning_with_active_purchase_order(self):
        """Reassign wizard should list the POs that will be cancelled."""
        fso = self._create_fso_with_po()
        purchase_order = fso.purchase_order_ids
        wizard = self.env["fsm.order.reassign.confirm"].create(
            {
                "fsm_order_id": fso.id,
                "new_person_id": self.internal_worker.id,
            }
        )

        self.assertEqual(wizard.purchase_order_ids, purchase_order)
        self.assertIn(purchase_order.name, wizard.warning_message)

    def test_reassign_wizard_warning_with_posted_bill(self):
        """Posted vendor bills should block automatic PO cancellation."""
        fso = self._create_fso_with_po()
        purchase_order = fso.purchase_order_ids
        self._create_posted_vendor_bill(purchase_order)
        wizard = self.env["fsm.order.reassign.confirm"].create(
            {
                "fsm_order_id": fso.id,
                "new_person_id": self.internal_worker.id,
            }
        )

        self.assertIn("posted vendor bills", wizard.warning_message)
        with self.assertRaises(UserError):
            wizard.action_confirm()
        self.assertEqual(fso.person_id, self.subcontractor)

    def test_reassign_wizard_cancels_draft_bill_before_purchase_order(self):
        """Draft vendor bills should be cancelled before worker reassignment."""
        fso = self._create_fso_with_po()
        purchase_order = fso.purchase_order_ids
        bill = self._create_draft_vendor_bill(purchase_order)
        wizard = self.env["fsm.order.reassign.confirm"].create(
            {
                "fsm_order_id": fso.id,
                "new_person_id": self.internal_worker.id,
            }
        )

        wizard.action_confirm()

        self.assertEqual(bill.state, "cancel")
        self.assertEqual(purchase_order.state, "cancel")
        self.assertEqual(fso.person_id, self.internal_worker)

    def test_reassign_wizard_on_closed_stage_is_blocked(self):
        """Wizard should not reassign when the FSO stage is closed."""
        fso = self._create_fso_with_po()
        purchase_order = fso.purchase_order_ids
        fso.stage_id = self.closed_stage
        wizard = self.env["fsm.order.reassign.confirm"].create(
            {
                "fsm_order_id": fso.id,
                "new_person_id": self.internal_worker.id,
            }
        )

        with self.assertRaises(UserError):
            wizard.action_confirm()
        self.assertEqual(purchase_order.state, "draft")
        self.assertEqual(fso.person_id, self.subcontractor)

    def test_reassignment_with_skip_context(self):
        """Reassignment should succeed when skip_reassign_check is set."""
        fso = self._create_fso_with_po()
        fso.with_context(skip_reassign_check=True).write(
            {"person_id": self.internal_worker.id}
        )
        self.assertEqual(fso.person_id, self.internal_worker)

    def test_reassignment_without_wizard_is_blocked_with_cancelled_po(self):
        """Changing worker directly should be blocked when a PO was created."""
        fso = self._create_fso_with_po()
        fso._cancel_active_subcontract_purchase_orders()

        with self.assertRaises(UserError):
            fso.write({"person_id": self.internal_worker.id})

    def test_wizard_cancels_po(self):
        """Wizard action_confirm should cancel PO and reassign."""
        fso = self._create_fso_with_po()
        po = fso.purchase_order_ids

        wizard = self.env["fsm.order.reassign.confirm"].create(
            {
                "fsm_order_id": fso.id,
                "new_person_id": self.internal_worker.id,
            }
        )
        self.assertEqual(wizard.purchase_order_ids, po)
        wizard.action_confirm()
        self.assertEqual(po.state, "cancel")
        self.assertEqual(fso.person_id, self.internal_worker)

    def test_reassign_wizard_with_fsm_and_purchase_user(self):
        """FSM and Purchase user can cancel PO and reassign through wizard."""
        fso = self._create_fso_with_po()
        po = fso.purchase_order_ids

        wizard = (
            self.env["fsm.order.reassign.confirm"]
            .with_user(self.fsm_purchase_user)
            .create(
                {
                    "fsm_order_id": fso.id,
                    "new_person_id": self.internal_worker.id,
                }
            )
        )
        wizard.action_confirm()

        self.assertEqual(po.state, "cancel")
        self.assertEqual(fso.person_id, self.internal_worker)
