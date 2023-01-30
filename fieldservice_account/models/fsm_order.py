# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.base_geoengine import geo_model

ACCOUNT_STAGES = [('draft', 'Draft'),
                  ('review', 'Needs Review'),
                  ('confirmed', 'Confirmed'),
                  ('invoiced', 'Fully Invoiced'),
                  ('no', 'Nothing Invoiced')]


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
    contractor_total = fields.Float(compute='_compute_contractor_cost',
                                    string='Contractor Cost Estimate')
    employee_time_total = fields.Float(compute='_compute_employee_hours',
                                       string='Total Employee Hours')
    account_stage = fields.Selection(ACCOUNT_STAGES, string='State',
                                     default='draft', required=True,
                                     readonly=True, store=True)

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

    @api.depends('employee_timesheet_ids')
    def _compute_employee_hours(self):
        for order in self:
            order.employee_time_total = 0.0
            for line in order.employee_timesheet_ids:
                order.employee_time_total += line.unit_amount

    @api.depends('contractor_cost_ids')
    def _compute_contractor_cost(self):
        for order in self:
            order.contractor_total = 0.0
            for cost in order.contractor_cost_ids:
                order.contractor_total += cost.price_unit * cost.quantity

    def action_complete(self):
        for order in self:
            order.account_stage = 'review'
        return super(FSMOrder, self).action_complete()

    def create_bills(self):
        jrnl = self.env['account.journal'].search([('type', '=', 'purchase'),
                                                   ('active', '=', True), ],
                                                  limit=1)
        fpos = self.customer_id.property_account_position_id
        vals = {
            'partner_id': self.person_id.partner_id.id,
            'type': 'in_invoice',
            'journal_id': jrnl.id or False,
            'fiscal_position_id': fpos.id or False,
            'fsm_order_id': self.id
        }

        bill = self.env['account.invoice'].sudo().create(vals)
        for line in self.contractor_cost_ids:
            line.invoice_id = bill
        bill.compute_taxes()

    def account_confirm(self):
        for order in self:
            contractor = order.person_id.partner_id.supplier
            if order.contractor_cost_ids and contractor:
                order.create_bills()
            order.account_stage = 'confirmed'

    def account_create_invoice(self):
        jrnl = self.env['account.journal'].search([('type', '=', 'sale'),
                                                  ('active', '=', True), ],
                                                  limit=1)
        fpos = self.customer_id.property_account_position_id
        vals = {
            'partner_id': self.customer_id.id,
            'type': 'out_invoice',
            'journal_id': jrnl.id or False,
            'fiscal_position_id': fpos.id or False,
            'fsm_order_id': self.id
        }

        invoice = self.env['account.invoice'].sudo().create(vals)
        price_list = invoice.partner_id.property_product_pricelist

        for line in self.employee_timesheet_ids:
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
        for cost in self.contractor_cost_ids:
            price = price_list.get_product_price(product=cost.product_id,
                                                 quantity=cost.quantity,
                                                 partner=invoice.partner_id,
                                                 date=False,
                                                 uom_id=False)
            template = cost.product_id.product_tmpl_id
            accounts = template.get_product_accounts()
            account = accounts['income']

            vals = {
                'product_id': cost.product_id.id,
                'account_analytic_id': cost.account_analytic_id.id,
                'quantity': cost.quantity,
                'name': cost.name,
                'price_unit': price,
                'account_id': account.id,
                'invoice_id': invoice.id,
            }
            con_cost = self.env['account.invoice.line'].create(vals)
            taxes = template.taxes_id
            con_cost.invoice_line_tax_ids = fpos.map_tax(taxes)
        invoice.compute_taxes()
        self.account_stage = 'invoiced'

    def account_no_invoice(self):
        self.account_stage = 'no'
