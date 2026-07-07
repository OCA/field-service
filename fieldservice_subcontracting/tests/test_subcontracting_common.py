# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class SubcontractingCommon(BaseCommon):
    @classmethod
    def _setup_subcontracting_data(
        cls,
        vendor_name="Test Vendor",
        worker_name="External Worker",
        order_type_name="Test Type",
        template_name="Test Template",
        duration=1.0,
    ):
        cls.vendor_partner = cls.env["res.partner"].create(
            {
                "name": vendor_name,
                "supplier_rank": 1,
            }
        )
        cls.location = cls.env["fsm.location"].create(
            {
                "name": "Test Location",
                "partner_id": cls.env["res.partner"].create({"name": "Client"}).id,
                "owner_id": cls.env["res.partner"]
                .create({"name": "Location Owner"})
                .id,
            }
        )
        cls.service_product = cls.env["product.product"].create(
            {
                "name": "Subcontracted Service",
                "type": "service",
                "purchase_method": "receive",
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
            }
        )
        cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.vendor_partner.id,
                "product_tmpl_id": cls.service_product.product_tmpl_id.id,
                "price": 100.0,
            }
        )
        cls.order_type = cls.env["fsm.order.type"].create(
            {
                "name": order_type_name,
            }
        )
        cls.template = cls.env["fsm.template"].create(
            {
                "name": template_name,
                "type_id": cls.order_type.id,
                "duration": duration,
                "subcontract_product_id": cls.service_product.id,
            }
        )
        cls.subcontractor = cls._create_worker(
            worker_name,
            partner=cls.vendor_partner,
            supplier_rank=1,
            is_fsm_subcontractor=True,
        )

    @classmethod
    def _create_worker(
        cls,
        name,
        partner=None,
        supplier_rank=None,
        is_fsm_subcontractor=None,
    ):
        if not partner:
            partner = cls.env["res.partner"].create({"name": name})
        vals = {
            "name": name,
            "partner_id": partner.id,
        }
        if supplier_rank is not None:
            vals["supplier_rank"] = supplier_rank
        if is_fsm_subcontractor is not None:
            vals["is_fsm_subcontractor"] = is_fsm_subcontractor
        return cls.env["fsm.person"].create(vals)

    @classmethod
    def _create_subcontracting_user(cls, login, *groups):
        return new_test_user(
            cls.env,
            login=login,
            groups=",".join(groups),
            password="TestUser1!",
        )

    @classmethod
    def _create_stage_with_action(cls, name, action_xmlid, **extra_vals):
        vals = {
            "name": name,
            "stage_type": "order",
            "action_id": cls.env.ref(action_xmlid).id,
        }
        vals.update(extra_vals)
        return cls.env["fsm.stage"].create(vals)

    def _create_fso(
        self,
        worker=None,
        order_type=None,
        template=None,
        project=None,
        scheduled_duration=1.0,
    ):
        vals = {
            "location_id": self.location.id,
        }
        if worker:
            vals["person_id"] = worker.id
        if order_type:
            vals["type"] = order_type.id
        if template:
            vals["template_id"] = template.id
        if project:
            vals["project_id"] = project.id
        if scheduled_duration is not None:
            vals["scheduled_duration"] = scheduled_duration
        return self.env["fsm.order"].create(vals)

    def _create_fso_with_po(self):
        fso = self._create_fso(
            worker=self.subcontractor,
            order_type=self.order_type,
            template=self.template,
        )
        fso._create_subcontract_po()
        self.assertTrue(fso.purchase_order_ids)
        return fso

    def _create_draft_vendor_bill(self, purchase_order):
        expense_account = self.env["account.account"].search(
            [("account_type", "=", "expense")],
            limit=1,
        )
        self.assertTrue(expense_account)
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": purchase_order.partner_id.id,
                "invoice_date": fields.Date.context_today(purchase_order),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": purchase_order.order_line.name,
                            "product_id": purchase_order.order_line.product_id.id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "purchase_line_id": purchase_order.order_line.id,
                            "account_id": expense_account.id,
                        },
                    )
                ],
            }
        )
        purchase_order.invalidate_recordset(["invoice_ids"])
        return bill

    def _create_posted_vendor_bill(self, purchase_order):
        bill = self._create_draft_vendor_bill(purchase_order)
        bill.action_post()
        purchase_order.invalidate_recordset(["invoice_ids"])
        return bill
