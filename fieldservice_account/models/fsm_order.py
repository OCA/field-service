# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.base_geoengine import geo_model


class FSMOrder(geo_model.GeoModel):
    _inherit = 'fsm.order'

    contractor_cost_ids = fields.One2many('account.invoice.line',
                                          'fsm_order_id',
                                          string='Contractor Costs')
    employee_timesheet_ids = fields.One2many('account.analytic.line',
                                             "fsm_order_id",
                                             string='Employee Timesheets')
    total_cost = fields.Float(compute='_compute_total_cost',
                              string='Total Cost')

    employee = fields.Boolean(compute='_compute_employee')

    def _compute_employee(self):
        user = self.env['res.users'].browse(self.env.uid)
        for order in self:
            if user.employee_ids:
                order.employee = True

    @api.depends('employee_timesheet_ids', 'contractor_cost_ids')
    def _compute_total_cost(self):
        for order in self:
            order.total_cost = 0.0
            for line in order.employee_timesheet_ids:
                for emp in line.user_id.employee_ids:
                    rate = emp.timesheet_cost
                    continue
                order.total_cost += line.unit_amount * rate
            for cost in order.contractor_cost_ids:
                order.total_cost += cost.price_unit * cost.quantity

    def action_complete(self):
        for order in self:
            if order.contractor_cost_ids:
                order._create_vendor_bill()
            if order.employee_timesheet_ids:
                order._create_customer_invoice()
        return super().action_complete()

    def _create_vendor_bill(self):
        jrnl = self.env['account.journal'].search([('type', '=', 'purchase'),
                                                  ('active', '=', True), ],
                                                  limit=1)
        fpos = self.customer_id.property_account_position_id
        vals = {
                'partner_id': self.person_id.partner_id.id,
                'type': 'in_invoice',
                'journal_id': jrnl.id or False,
                'fiscal_position_id': fpos.id or False
                }

        bill = self.env['account.invoice'].sudo().create(vals)
        for line in self.contractor_cost_ids:
            line.invoice_id = bill
        bill.compute_taxes()

    def _create_customer_invoice(self):
        jrnl = self.env['account.journal'].search([('type', '=', 'sale'),
                                                  ('active', '=', True), ],
                                                  limit=1)
        fpos = self.customer_id.property_account_position_id
        vals = {
                'partner_id': self.customer_id.id,
                'type': 'out_invoice',
                'journal_id': jrnl.id or False,
                'fiscal_position_id': fpos.id or False
                }

        invoice = self.env['account.invoice'].sudo().create(vals)

        for line in self.employee_timesheet_ids:
            price_list = invoice.partner_id.property_product_pricelist
            price = price_list.get_product_price(product=line.product_id,
                                                 quantity=line.unit_amount,
                                                 partner=invoice.partner_id,
                                                 date=False,
                                                 uom_id=False)
            template = line.product_id.product_tmpl_id
            accounts = template.get_product_accounts()
            account = accounts['income']

            vals = {
                    'product_id': line.product_id.id,
                    'account_analytic_id': line.account_id.id,
                    'quantity': line.unit_amount,
                    'name': line.name,
                    'price_unit': price,
                    'account_id': account.id,
                    'invoice_id': invoice.id,
            }
            time_cost = self.env['account.invoice.line'].create(vals)
            taxes = template.taxes_id
            time_cost.invoice_line_tax_ids = fpos.map_tax(taxes)
            time_cost.invoice_id = invoice
        invoice.compute_taxes()
