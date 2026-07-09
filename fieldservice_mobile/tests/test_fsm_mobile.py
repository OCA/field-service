# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
from datetime import datetime, timedelta

from odoo import Command
from odoo.exceptions import AccessError, UserError
from odoo.tests.common import users

from odoo.addons.fieldservice.tests.test_fsm_common import FSMCommon


class TestFieldserviceMobile(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Order = cls.env["fsm.order"]
        cls.Mapping = cls.env["fsm.mobile.feature.mapping"]
        cls.FeatureLine = cls.env["fsm.mobile.feature.line"]
        cls.StageHistory = cls.env["fsm.stage.history"]
        cls.order_stage = cls.env["fsm.stage"].create(
            {
                "name": "Mobile Order Stage",
                "sequence": 20,
                "stage_type": "order",
                "is_display_in_mobile": True,
                "is_display_in_odoo": True,
            }
        )
        cls.portal_user = cls.env["res.users"].create(
            {
                "name": "FSM Portal User",
                "login": "fsm_mobile_portal_user",
                "group_ids": [(6, 0, [cls.env.ref("base.group_portal").id])],
            }
        )
        cls.manager_group = cls.env.ref("fieldservice.group_fsm_manager")
        cls.env.user.write({"group_ids": [(4, cls.manager_group.id)]})
        cls.feature_line = cls.FeatureLine.create(
            {
                "name": "Test Feature",
                "code": "TST",
                "group_ids": [(6, 0, [cls.manager_group.id])],
            }
        )
        cls.feature_mapping = cls.Mapping.create(
            {
                "name": "Test Mapping",
                "feature_line_ids": [(6, 0, [cls.feature_line.id])],
                "installed_module_ids": [
                    (6, 0, [cls.env.ref("base.module_fieldservice").id])
                ],
            }
        )
        cls.test_location.write(
            {
                "partner_id": cls.portal_user.partner_id.id,
                "owner_id": cls.portal_user.partner_id.id,
            }
        )
        cls.test_order = cls.Order.create(
            {
                "location_id": cls.test_location.id,
                "stage_id": cls.order_stage.id,
            }
        )
        cls.payment_method = cls.env.ref("payment.payment_method_unknown")
        cls.payment_provider = (
            cls.env["payment.provider"]
            .sudo()
            .create(
                {
                    "name": "FSM Mobile Test Provider",
                    "code": "none",
                    "state": "test",
                    "is_published": True,
                    "payment_method_ids": [Command.set(cls.payment_method.ids)],
                }
            )
        )
        cls.payment_method.sudo().write({"active": True})

    def _create_payment_transaction(
        self, sale_order, state="done", reference="TEST", confirm=True
    ):
        if confirm:
            sale_order.action_confirm()
        transaction = self.env["payment.transaction"].create(
            {
                "provider_id": self.payment_provider.id,
                "payment_method_id": self.payment_method.id,
                "reference": reference,
                "amount": sale_order.amount_total,
                "currency_id": sale_order.currency_id.id,
                "partner_id": sale_order.partner_id.id,
                "sale_order_ids": [Command.set([sale_order.id])],
                "operation": "online_direct",
            }
        )
        transaction.write({"state": state})
        sale_order.invalidate_recordset(["transaction_ids"])
        return transaction

    def test_fsm_stage_mobile_flags(self):
        stage = self.env["fsm.stage"].create(
            {
                "name": "Mobile Stage",
                "sequence": 30,
                "stage_type": "order",
                "is_display_in_mobile": True,
                "is_display_in_odoo": False,
            }
        )
        self.assertTrue(stage.is_display_in_mobile)
        self.assertFalse(stage.is_display_in_odoo)

    def test_stage_history_and_duration(self):
        start = datetime.now() - timedelta(hours=2)
        end = datetime.now()
        history = self.StageHistory.create(
            {
                "order_id": self.test_order.id,
                "start_datetime": start,
                "stage_id": self.order_stage.id,
                "duration": 1.0,
                "total_duration": 2.5,
            }
        )
        self.test_order.write({"date_end": end})
        self.test_order.flush_recordset()
        self.assertEqual(self.test_order.duration, history.total_duration)

    def test_duration_without_end_date(self):
        order = self.Order.create({"location_id": self.test_location.id})
        self.assertEqual(order.duration, 0.0)

    def test_feature_mapping_display_name(self):
        mapping = self.Mapping.create({"name": "Display Name Mapping"})
        self.assertEqual(mapping.display_name, "Display Name Mapping")

    def test_feature_mapping_workflow(self):
        mapping = self.Mapping.create({"name": "Draft Mapping"})
        mapping.set_to_draft()
        self.assertEqual(mapping.state, "draft")
        mapping.set_to_active()
        self.assertEqual(mapping.state, "active")
        with self.assertRaises(UserError):
            self.Mapping.create({"name": "Second Active"}).set_to_active()
        mapping.set_to_draft()
        mapping.unlink()

    def test_feature_mapping_unlink_active(self):
        mapping = self.Mapping.create({"name": "Active Delete Test"})
        mapping.set_to_active()
        with self.assertRaises(UserError):
            mapping.unlink()
        mapping.set_to_draft()

    def test_feature_mapping_values_for_user(self):
        self.Mapping.search([("state", "=", "active")]).set_to_draft()
        line = self.FeatureLine.create(
            {
                "name": "User Feature",
                "code": "USR",
                "group_ids": [(6, 0, [self.manager_group.id])],
            }
        )
        mapping = self.Mapping.create(
            {
                "name": "Values Mapping",
                "feature_line_ids": [(6, 0, [line.id])],
                "installed_module_ids": [
                    (6, 0, [self.env.ref("base.module_fieldservice").id])
                ],
                "state": "active",
            }
        )
        self.assertEqual(mapping.state, "active")
        values = self.Mapping.get_fsm_mobile_feature_mapping_values(self.env.user.id)
        self.assertIn("feature_mapping", values)
        self.assertIn("installed_modules", values)
        self.assertEqual(values["feature_mapping"][0]["code"], "USR")

    def test_feature_mapping_values_without_active_record(self):
        self.assertEqual(self.Mapping.get_fsm_mobile_feature_mapping_values(1), {})

    def test_feature_mapping_values_without_installed_modules(self):
        self.Mapping.search([("state", "=", "active")]).set_to_draft()
        line = self.FeatureLine.create(
            {
                "name": "No Module Feature",
                "code": "NOM",
                "group_ids": [(6, 0, [self.manager_group.id])],
            }
        )
        self.Mapping.create(
            {
                "name": "No Modules Mapping",
                "feature_line_ids": [(6, 0, [line.id])],
                "state": "active",
            }
        )
        values = self.Mapping.get_fsm_mobile_feature_mapping_values(self.env.user.id)
        self.assertEqual(values, {})

    def test_feature_mapping_values_without_matching_groups(self):
        self.Mapping.search([("state", "=", "active")]).set_to_draft()
        line = self.FeatureLine.create(
            {
                "name": "Portal Feature",
                "code": "POR",
                "group_ids": [(6, 0, [self.manager_group.id])],
            }
        )
        self.Mapping.create(
            {
                "name": "Portal Mapping",
                "feature_line_ids": [(6, 0, [line.id])],
                "installed_module_ids": [
                    (6, 0, [self.env.ref("base.module_fieldservice").id])
                ],
                "state": "active",
            }
        )
        values = self.Mapping.get_fsm_mobile_feature_mapping_values(self.portal_user.id)
        self.assertEqual(values, {})

    def test_duration_with_end_date_without_history(self):
        order = self.Order.create(
            {
                "location_id": self.test_location.id,
                "date_end": datetime.now(),
            }
        )
        self.assertFalse(order.duration)

    def test_create_fsm_attachment(self):
        attachment_id = self.Order.create_fsm_attachment(
            "test.txt",
            base64.b64encode(b"test"),
            "fsm.order",
            self.test_order.id,
        )
        attachment = self.env["ir.attachment"].browse(attachment_id)
        self.assertEqual(attachment.res_model, "fsm.order")
        self.assertEqual(attachment.res_id, self.test_order.id)
        self.assertFalse(self.Order.create_fsm_attachment("x", b"x", "res.partner", 1))

    def test_portal_attachment_access(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "portal.txt",
                "datas": base64.b64encode(b"portal"),
                "res_model": "fsm.order",
                "res_id": self.test_order.id,
            }
        )
        attachment.with_user(self.portal_user).read(["name"])

    def test_portal_attachment_field_access_denied(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "field.bin",
                "datas": base64.b64encode(b"data"),
                "res_model": "fsm.order",
                "res_id": self.test_order.id,
                "res_field": "signature",
            }
        )
        with self.assertRaises(AccessError):
            attachment.with_user(self.portal_user).check("read")
        with self.assertRaises(AccessError):
            attachment.with_user(self.portal_user)._fsm_check_attachment_access("read")

    def test_attachment_public_read_skips_linked_check(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "public.txt",
                "datas": base64.b64encode(b"public"),
                "public": True,
                "res_model": "fsm.order",
                "res_id": self.test_order.id,
            }
        )
        attachment._fsm_check_attachment_access("read")

    def test_attachment_check_values_without_record(self):
        self.env["ir.attachment"]._fsm_check_attachment_access(
            "read",
            values={
                "res_model": "fsm.order",
                "res_id": self.test_order.id,
            },
        )

    def test_attachment_check_superuser(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "super.txt",
                "datas": base64.b64encode(b"super"),
                "res_model": "fsm.order",
                "res_id": self.test_order.id,
            }
        )
        self.assertTrue(attachment.sudo().check("read"))

    def test_attachment_check_unlink_mode(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "unlink.txt",
                "datas": base64.b64encode(b"unlink"),
                "res_model": "fsm.order",
                "res_id": self.test_order.id,
            }
        )
        self.assertTrue(attachment.check("unlink"))

    def test_attachment_check_create_mode(self):
        self.assertTrue(
            self.env["ir.attachment"].check(
                "create",
                values={
                    "res_model": "fsm.order",
                    "res_id": self.test_order.id,
                },
            )
        )

    def test_attachment_check_unknown_model(self):
        self.assertTrue(
            self.env["ir.attachment"].check(
                "read",
                values={"res_model": "unknown.model", "res_id": 1},
            )
        )

    def test_attachment_check_unknown_model_on_record(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "unknown-model.txt",
                "datas": base64.b64encode(b"unknown"),
                "res_model": "unknown.model",
                "res_id": 1,
            }
        )
        attachment._fsm_check_attachment_access("read")

    def test_attachment_check_linked_record_read(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "linked.txt",
                "datas": base64.b64encode(b"linked"),
                "res_model": "fsm.order",
                "res_id": self.test_order.id,
            }
        )
        attachment._fsm_check_attachment_access("read")
        attachment._fsm_check_attachment_access("write")
        attachment._fsm_check_attachment_access("unlink")
        self.assertTrue(attachment.check("read"))

    def test_attachment_without_linked_record(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "standalone.txt",
                "datas": base64.b64encode(b"standalone"),
            }
        )
        attachment._fsm_check_attachment_access("read")
        self.assertTrue(attachment.check("read"))

    def test_attachment_check_public_read(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "public.txt",
                "datas": base64.b64encode(b"public"),
                "public": True,
            }
        )
        attachment.with_user(self.portal_user).check("read")

    def test_attachment_check_values_on_create(self):
        self.env["ir.attachment"].check(
            "read",
            values={
                "res_model": "fsm.order",
                "res_id": self.test_order.id,
            },
        )

    def test_attachment_check_own_user_record(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "user.png",
                "datas": base64.b64encode(b"img"),
                "res_model": "res.users",
                "res_id": self.env.user.id,
            }
        )
        attachment.check("write")

    def test_attachment_check_portal_user_own_record(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "portal-user.png",
                "datas": base64.b64encode(b"img"),
                "res_model": "res.users",
                "res_id": self.portal_user.id,
            }
        )
        attachment.with_user(self.portal_user).check("read")

    def test_get_portal_config_values(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "fieldservice_mobile.fsm_allow_portal_view_move_qty", "True"
        )
        values = self.env["res.users"].get_portal_config_values(
            ["fieldservice_mobile.fsm_allow_portal_view_move_qty"]
        )
        self.assertTrue(values["fieldservice_mobile.fsm_allow_portal_view_move_qty"])

    def test_get_portal_config_values_ignores_unknown(self):
        values = self.env["res.users"].get_portal_config_values(["unknown.param"])
        self.assertEqual(values, {})

    def test_get_portal_config_values_empty_parameters(self):
        values = self.env["res.users"].get_portal_config_values([])
        self.assertEqual(values, {})

    def test_payment_state_not_paid(self):
        sale_order = self.env["sale.order"].create({"partner_id": self.test_partner.id})
        order = self.Order.create(
            {
                "location_id": self.test_location.id,
                "sale_id": sale_order.id,
            }
        )
        self.assertEqual(order.payment_state, "not_paid")

    def _create_sale_order(self):
        product = self.env["product.product"].create({"name": "FSM Mobile Service"})
        return self.env["sale.order"].create(
            {
                "partner_id": self.test_partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )

    def test_payment_state_partial_paid(self):
        sale_order = self._create_sale_order()
        order = self.Order.create(
            {
                "location_id": self.test_location.id,
                "sale_id": sale_order.id,
            }
        )
        self._create_payment_transaction(
            sale_order, state="pending", reference="TEST-TXN-PENDING"
        )
        self.assertTrue(sale_order.transaction_ids)
        order._compute_payment_state()
        self.assertEqual(order.payment_state, "pending")

    def test_payment_state_paid_and_pending(self):
        sale_order = self._create_sale_order()
        order = self.Order.create(
            {
                "location_id": self.test_location.id,
                "sale_id": sale_order.id,
            }
        )
        self._create_payment_transaction(
            sale_order, state="done", reference="TEST-TXN-1"
        )
        self.assertTrue(sale_order.transaction_ids)
        order._compute_payment_state()
        self.assertEqual(order.payment_state, "paid")
        sale_order.transaction_ids.write({"state": "pending"})
        order._compute_payment_state()
        self.assertEqual(order.payment_state, "pending")

    def test_payment_state_mixed_transactions(self):
        sale_order = self._create_sale_order()
        order = self.Order.create(
            {
                "location_id": self.test_location.id,
                "sale_id": sale_order.id,
            }
        )
        self._create_payment_transaction(
            sale_order, state="done", reference="TEST-TXN-DONE"
        )
        self._create_payment_transaction(
            sale_order, state="cancel", reference="TEST-TXN-CANCEL", confirm=False
        )
        order._compute_payment_state()
        self.assertEqual(order.payment_state, "not_paid")

    def test_generate_so_payment_link_without_sale(self):
        result = self.Order.generate_so_payment_link(self.test_order.id)
        self.assertFalse(result["payment_status"])

    def test_generate_so_payment_link_with_sale(self):
        product = self.env["product.product"].create({"name": "FSM Service"})
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.test_partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        order = self.Order.create(
            {
                "location_id": self.test_location.id,
                "sale_id": sale_order.id,
            }
        )
        result = self.Order.generate_so_payment_link(order.id)
        self.assertTrue(result["payment_status"])
        self.assertTrue(result["payment_link"])

    @users("admin")
    def test_config_settings_fields(self):
        settings = self.env["res.config.settings"].create(
            {
                "fsm_allow_portal_view_move_qty": True,
                "fsm_allow_portal_update_move_qty": True,
            }
        )
        settings.execute()
        icp = self.env["ir.config_parameter"].sudo()
        self.assertTrue(
            icp.get_param("fieldservice_mobile.fsm_allow_portal_view_move_qty")
        )
        self.assertTrue(
            icp.get_param("fieldservice_mobile.fsm_allow_portal_update_move_qty")
        )
