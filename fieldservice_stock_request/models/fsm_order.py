# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.exceptions import UserError


REQUEST_STATES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('open', 'In progress'),
    ('done', 'Done'),
    ('cancel', 'Cancelled')]


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    stock_request_ids = fields.One2many('stock.request', 'fsm_order_id',
                                        string="Order Lines")
    request_stage = fields.Selection(REQUEST_STATES, string='Request State',
                                     default='draft', readonly=True,
                                     store=True)

    @api.multi
    def action_request_submit(self):
        for rec in self:
            if not rec.stock_request_ids:
                raise UserError(_('Please create a stock request.'))
            for line in rec.stock_request_ids:
                if line.state == 'draft':
                    if line.order_id:
                        line.order_id.action_submit()
                    else:
                        line.action_submit()
            rec.request_stage = 'submitted'

    @api.multi
    def action_request_cancel(self):
        for rec in self:
            if not rec.stock_request_ids:
                raise UserError(_('Please create a stock request.'))
            for line in rec.stock_request_ids:
                if line.state in ('draft', 'submitted'):
                    if line.order_id:
                        line.order_id.action_cancel()
                    else:
                        line.action_cancel()
            rec.request_stage = 'cancel'

    @api.multi
    def action_request_draft(self):
        for rec in self:
            if not rec.stock_request_ids:
                raise UserError(_('Please create a stock request.'))
            for line in rec.stock_request_ids:
                if line.state == 'cancel':
                    if line.order_id:
                        line.order_id.action_draft()
                    else:
                        line.action_draft()
            rec.request_stage = 'draft'
