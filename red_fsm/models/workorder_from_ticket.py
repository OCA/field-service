# -*- coding: utf-8 -*-

from odoo import fields, models


class FsmOrderExtended(models.Model):
    _inherit = 'fsm.order'

    ticket_id = fields.Many2one(
        'website.support.ticket',
        string="Support Ticket"
    )

    def action_open_ticket(self):
        """
        open the related ticket form.
        """
        return {
            'name': 'Support Ticket',
            'type': 'ir.actions.act_window',
            'res_model': 'website.support.ticket',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.ticket_id.id
        }


class SupportTicketExtend(models.Model):
    _inherit = 'website.support.ticket'

    workorder_count = fields.Integer(
        string="Work-order count",
        compute='find_workorder_count'
    )

    def find_workorder_count(self):
        """Computes the count of related work-orders"""
        cr = self._cr
        cr.execute("SELECT COUNT(*) "
                   "FROM fsm_order "
                   "WHERE ticket_id=%s",
                   (self.id, ))
        order_count = cr.fetchone()
        self.workorder_count = order_count and order_count[0] or 0
        return False

    def action_open_workorder(self):
        """We are opening a work order form with the
        details provided on the ticket"""
        return {
            'name': 'Workorder',
            'type': 'ir.actions.act_window',
            'res_model': 'fsm.order',
            'view_type': 'form',
            'view_mode': 'form',
            'context': {
                'default_name': self.subject,
                'default_description': self.description,
                'default_requested_date': self.create_date,
                'default_customer_id': self.partner_id.id,
                'default_ticket_id': self.id
            }
        }

    def action_open_related_orders(self):
        """
        open the related work orders list.
        """
        self.ensure_one()
        return {
            'name': 'Work-Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'fsm.order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('ticket_id', '=', self.id)]
        }
