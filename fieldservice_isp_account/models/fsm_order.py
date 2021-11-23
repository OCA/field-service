# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

ACCOUNT_STAGES = [
    ("draft", "Draft"),
    ("review", "Needs Review"),
    ("confirmed", "Confirmed"),
    ("invoiced", "Fully Invoiced"),
    ("no", "Nothing Invoiced"),
]


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    contractor_cost_ids = fields.One2many(
        "fsm.order.cost", "fsm_order_id", string="Contractor Costs"
    )
    employee_timesheet_ids = fields.One2many(
        "account.analytic.line", "fsm_order_id", string="Employee Timesheets"
    )
    employee = fields.Boolean(compute="_compute_employee")
    contractor_total = fields.Float(
        compute="_compute_contractor_cost", string="Contractor Cost Estimate"
    )
    employee_time_total = fields.Float(
        compute="_compute_employee_hours", string="Total Employee Hours"
    )
    account_stage = fields.Selection(
        ACCOUNT_STAGES, string="Accounting Stage", default="draft"
    )

    def _compute_employee(self):
        user = self.env["res.users"].browse(self.env.uid)
        for order in self:
            if user.employee_ids:
                order.employee = True
            else:
                order.employee = False

    @api.depends("employee_timesheet_ids", "contractor_cost_ids")
    def _compute_total_cost(self):
        super()._compute_total_cost()
        for order in self:
            order.total_cost = 0.0
            rate = 0
            for line in order.employee_timesheet_ids:
                rate = line.employee_id.timesheet_cost
                order.total_cost += line.unit_amount * rate
            for cost in order.contractor_cost_ids:
                order.total_cost += cost.price_unit * cost.quantity

    @api.depends("employee_timesheet_ids")
    def _compute_employee_hours(self):
        for order in self:
            order.employee_time_total = 0.0
            for line in order.employee_timesheet_ids:
                order.employee_time_total += line.unit_amount

    @api.depends("contractor_cost_ids")
    def _compute_contractor_cost(self):
        for order in self:
            order.contractor_total = 0.0
            for cost in order.contractor_cost_ids:
                order.contractor_total += cost.price_unit * cost.quantity

    def action_complete(self):
        for order in self:
            order.account_stage = "review"
        if self.person_id.supplier_rank and not self.contractor_cost_ids:
            raise ValidationError(
                _("Cannot move to Complete " + "until 'Contractor Costs' is filled in")
            )
        if not self.person_id.supplier_rank and not self.employee_timesheet_ids:
            raise ValidationError(
                _(
                    "Cannot move to Complete until "
                    + "'Employee Timesheets' is filled in"
                )
            )
        return super(FSMOrder, self).action_complete()

    def create_bills(self):
        jrnl = self.env["account.journal"].search(
            [
                ("company_id", "=", self.env.company.id),
                ("type", "=", "purchase"),
                ("active", "=", True),
            ],
            limit=1,
        )
        fpos = self.person_id.partner_id.property_account_position_id
        invoice_line_vals = []
        for cost in self.contractor_cost_ids:
            invoice_line_vals.append((0, 0, self._get_bill_line_vals(cost, fpos)))
        vals = {
            "partner_id": self.person_id.partner_id.id,
            "type": "in_invoice",
            "journal_id": jrnl.id or False,
            "fiscal_position_id": fpos.id or False,
            "fsm_order_ids": [(4, self.id)],
            "company_id": self.env.company.id,
            "invoice_line_ids": invoice_line_vals,
        }
        bill = self.env["account.move"].sudo().create(vals)
        bill._recompute_tax_lines()

    def _get_bill_line_vals(self, cost, fpos):
        template = cost.product_id.product_tmpl_id
        accounts = template.get_product_accounts()
        account = accounts["expense"]
        taxes = template.supplier_taxes_id
        tax_ids = fpos.map_tax(taxes)
        return {
            "analytic_account_id": self.location_id.analytic_account_id.id,
            "product_id": cost.product_id.id,
            "product_uom_id": cost.product_id.uom_id.id,
            "quantity": cost.quantity,
            "name": cost.product_id.display_name,
            "price_unit": cost.price_unit,
            "account_id": account.id,
            "fsm_order_ids": [(4, self.id)],
            "tax_ids": [(6, 0, tax_ids.ids)],
        }

    def account_confirm(self):
        for order in self:
            contractor = order.person_id.partner_id.supplier_rank
            if order.contractor_cost_ids:
                if contractor:
                    order.create_bills()
                    order.account_stage = "confirmed"
                else:
                    raise ValidationError(
                        _("The worker assigned to this order" " is not a supplier")
                    )
            if order.employee_timesheet_ids:
                order.account_stage = "confirmed"

    def _get_invoice_line_vals(self, fpos, price_list, invoice_vals):
        invoice_line_vals = []
        for cost in self.contractor_cost_ids:
            invoice_line_vals.append(
                (
                    0,
                    0,
                    self._get_cost_invoice_line_vals(
                        cost, fpos, price_list, invoice_vals
                    ),
                )
            )
        for line in self.employee_timesheet_ids:
            invoice_line_vals.append(
                (
                    0,
                    0,
                    self._get_timesheet_line_invoice_line_vals(
                        line, fpos, price_list, invoice_vals
                    ),
                )
            )
        return invoice_line_vals

    def account_create_invoice(self):
        fpos = self._get_fpos()
        invoice_vals = self._get_invoice_vals(fpos)
        price_list = self._get_pricelist()
        invoice_line_vals = self._get_invoice_line_vals(fpos, price_list, invoice_vals)
        invoice_vals.update({"invoice_line_ids": invoice_line_vals})
        invoice = self.env["account.move"].sudo().create(invoice_vals)
        invoice._recompute_tax_lines()
        self.account_stage = "invoiced"
        return invoice

    def _get_pricelist(self):
        if self.bill_to == "customer":
            if not self.customer_id:
                raise ValidationError(_("Customer empty"))
            return self.customer_id.property_product_pricelist
        elif self.bill_to == "location":
            return self.location_id.customer_id.property_product_pricelist

    def _get_fpos(self):
        if self.bill_to == "customer":
            if not self.customer_id:
                raise ValidationError(_("Customer empty"))
            return self.customer_id.property_account_position_id
        elif self.bill_to == "location":
            return self.location_id.customer_id.property_account_position_id

    def _get_invoice_vals(self, fpos):
        jrnl = self.env["account.journal"].search(
            [
                ("company_id", "=", self.env.company.id),
                ("type", "=", "sale"),
                ("active", "=", True),
            ],
            limit=1,
        )
        invoice_vals = {
            "journal_id": jrnl.id or False,
            "type": "out_invoice",
            "fiscal_position_id": fpos.id or False,
            "fsm_order_ids": [(4, self.id)],
        }
        if self.bill_to == "customer":
            if not self.customer_id:
                raise ValidationError(_("Customer empty"))
            invoice_vals.update({
                "partner_id": self.customer_id.id,
            })
        elif self.bill_to == "location":
            invoice_vals.update({
                "partner_id": self.location_id.customer_id.id,
                "company_id": self.env.company.id,
            })
        return invoice_vals

    def _get_cost_invoice_line_vals(self, cost, fpos, price_list, invoice_vals):
        price = price_list.get_product_price(
            product=cost.product_id,
            quantity=cost.quantity,
            partner=invoice_vals.get("partner_id"),
            date=False,
            uom_id=False,
        )
        template = cost.product_id.product_tmpl_id
        accounts = template.get_product_accounts()
        account = accounts["income"]
        taxes = template.taxes_id
        tax_ids = fpos.map_tax(taxes)
        return {
            "product_id": cost.product_id.id,
            "product_uom_id": cost.product_id.uom_id.id,
            "analytic_account_id": self.location_id.analytic_account_id.id,
            "quantity": cost.quantity,
            "name": cost.product_id.display_name,
            "price_unit": price,
            "account_id": account.id,
            "fsm_order_ids": [(4, self.id)],
            "tax_ids": [(6, 0, tax_ids.ids)],
        }

    def _get_timesheet_line_invoice_line_vals(
        self, line, fpos, price_list, invoice_vals
    ):
        price = price_list.get_product_price(
            product=line.product_id,
            quantity=line.unit_amount,
            partner=invoice_vals.get("partner_id"),
            date=False,
            uom_id=False,
        )
        template = line.product_id.product_tmpl_id
        accounts = template.get_product_accounts()
        account = accounts["income"]
        taxes = template.taxes_id
        tax_ids = fpos.map_tax(taxes)
        return {
            "product_id": line.product_id.id,
            "product_uom_id": line.product_id.uom_id.id,
            "analytic_account_id": line.account_id.id,
            "quantity": line.unit_amount,
            "name": line.name,
            "price_unit": price,
            "account_id": account.id,
            "fsm_order_ids": [(4, self.id)],
            "tax_ids": [(6, 0, tax_ids.ids)],
        }

    def account_no_invoice(self):
        self.account_stage = "no"
