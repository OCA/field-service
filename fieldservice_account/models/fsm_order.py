# Copyright (C) 2018 - TODAY, Open Source Integrators
# Copyright (C) 2019, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


ACCOUNT_STAGES = [('draft', 'Draft'),
                  ('review', 'Needs Review'),
                  ('confirmed', 'Confirmed'),
                  ('invoiced', 'Fully Invoiced'),
                  ('no', 'Nothing Invoiced')]


class FSMOrder(models.Model):
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
    account_stage = fields.Selection(ACCOUNT_STAGES, string='Accounting Stage',
                                     default='draft')
    bill_to = fields.Selection([('location', 'Bill Location'),
                                ('contact', 'Bill Contact')],
                               string='Bill to',
                               required=True,
                               default='location')
    customer_id = fields.Many2one('res.partner', string='Contact',
                                  domain=[('customer', '=', True)],
                                  change_default=True,
                                  index=True,
                                  track_visibility='always')
    cost_method = fields.Selection([('timesheet', 'Timesheets'),
                                    ('fixed', 'Fixed Rate')],
                                   string='Cost Method',
                                   required=True,
                                   default='timesheet')
    fixed_cost = fields.Float(string='Fixed Cost')
    product_id = fields.Many2one('product.product', string='Invoice Product')
    invoice_id = fields.Many2one('account.invoice', string='Customer Invoice',
                                 domain="[('type', '=', 'out_invoice')")
    bill_id = fields.Many2one('account.invoice', string='Vendor Bill',
                              domain="[('type', '=', 'in'_invoice')]")

    def _compute_employee(self):
        user = self.env['res.users'].browse(self.env.uid)
        for order in self:
            if user.employee_ids:
                order.employee = True

    @api.depends('employee_timesheet_ids', 'contractor_cost_ids', 'fixed_cost')
    def _compute_total_cost(self):
        for order in self:
            order.total_cost = 0.0
            rate = 0
            if order.cost_method == 'timesheet':
                for line in order.employee_timesheet_ids:
                    rate = line.employee_id.timesheet_cost
                    order.total_cost += line.unit_amount * rate
                for cost in order.contractor_cost_ids:
                    order.total_cost += cost.price_unit * cost.quantity
            elif order.cost_method == 'fixed':
                order.total_cost = order.fixed_cost

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
            if order.cost_method == 'timesheet':
                if order.person_id.supplier and not order.contractor_cost_ids:
                    raise ValidationError(_("""
                        Cannot move to Complete until 'Contractor Costs'
                        is filled in"""))
                if not order.person_id.supplier and \
                   not order.employee_timesheet_ids:
                    raise ValidationError(_("""
                        Cannot move to Complete until 'Employee Timesheets'
                        is filled in"""))
        return super(FSMOrder, self).action_complete()

    def create_bill(self):
        jrnl = self.env['account.journal'].search([
            ('company_id', '=', self.env.user.company_id.id),
            ('type', '=', 'purchase'),
            ('active', '=', True)],
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
        self.bill_id = bill.id

    def account_confirm(self):
        for order in self:
            if order.cost_method == 'timesheet':
                contractor = order.person_id.partner_id.supplier
                if order.contractor_cost_ids:
                    if contractor:
                        order.create_bill()
                        order.account_stage = 'confirmed'
                    else:
                        raise ValidationError(_("""
                            The worker assigned to this order
                            is not a supplier"""))
                if order.employee_timesheet_ids:
                    order.account_stage = 'confirmed'
            elif order.cost_method == 'fixed':
                order.account_stage = 'confirmed'

    def account_create_invoice(self):
        jrnl = self.env['account.journal'].search([
            ('company_id', '=', self.env.user.company_id.id),
            ('type', '=', 'sale'),
            ('active', '=', True)],
            limit=1)
        inv_partner = False
        if self.bill_to == 'contact':
            if not self.customer_id:
                raise ValidationError(_("Contact empty"))
            inv_partner = self.customer_id
        else:
            inv_partner = self.location_id.customer_id
        fpos = inv_partner.property_account_position_id
        vals = {
            'partner_id': inv_partner.id,
            'type': 'out_invoice',
            'journal_id': jrnl.id or False,
            'fiscal_position_id': fpos.id or False,
            'fsm_order_id': self.id
        }
        invoice = self.env['account.invoice'].sudo().create(vals)
        price_list = invoice.partner_id.property_product_pricelist
        if self.cost_method == 'timesheet':
            for line in self.employee_timesheet_ids:
                price = price_list.get_product_price(
                    product=line.product_id,
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
                    'invoice_id': invoice.id
                }
                time_cost = self.env['account.invoice.line'].create(vals)
                taxes = template.taxes_id
                time_cost.invoice_line_tax_ids = fpos.map_tax(taxes)
            for cost in self.contractor_cost_ids:
                price = price_list.get_product_price(
                    product=cost.product_id,
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
                    'invoice_id': invoice.id
                }
                con_cost = self.env['account.invoice.line'].create(vals)
                taxes = template.taxes_id
                con_cost.invoice_line_tax_ids = fpos.map_tax(taxes)
        elif self.cost_method == 'fixed':
            price = self.fixed_cost
            template = self.product_id.product_tmpl_id
            accounts = template.get_product_accounts()
            account = accounts['income']
            analytic = self.location_id.analytic_account_id
            vals = {
                'product_id': self.product_id.id,
                'account_analytic_id': analytic.id,
                'quantity': 1,
                'name': template.name,
                'price_unit': price,
                'account_id': account.id,
                'invoice_id': invoice.id
            }
            fixed = self.env['account.invoice.line'].create(vals)
            taxes = template.taxes_id
            fixed.invoice_line_tax_ids = fpos.map_tax(taxes)
        invoice.compute_taxes()
        self.account_stage = 'invoiced'
        self.invoice_id = invoice.id
        return invoice

    def account_no_invoice(self):
        self.account_stage = 'no'

    @api.onchange('location_id')
    def _onchange_location_id_customer_account(self):
        if self.location_id:
            return {'domain': {'customer_id': [('service_location_id', '=',
                                                self.location_id.name)]}}
        else:
            return {'domain': {'customer_id': [('id', '!=', None)]}}

    @api.onchange('customer_id')
    def _onchange_customer_id_location(self):
        if self.customer_id:
            self.location_id = self.customer_id.service_location_id

    @api.multi
    def write(self, vals):
        res = super(FSMOrder, self).write(vals)
        for order in self:
            if 'customer_id' not in vals and order.customer_id is False:
                order.customer_id = order.location_id.customer_id.id
        return res
