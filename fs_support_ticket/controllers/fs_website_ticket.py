# -*- coding: utf-8 -*-

import base64

from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.tools.translate import _


class SupportTicket(http.Controller):
    @http.route(['/fs/ticket'], type='http', auth="public", website=True)
    def field_service_ticket(self, **kwargs):
        ticket_categ = request.env['fsm.ticket.category'].sudo().search([])
        customer_name = ''
        if request.env.user:
            if request.env.user.name != 'Public user':
                customer_name = request.env.user.name

        values = {
            'ticket_categ': ticket_categ or [],
            'customer_name': customer_name,
            'email': request.env.user and request.env.user.partner_id.email or '',
        }

        return request.render("fs_support_ticket.fs_tickets", values)

    @http.route(['/fs/ticket/submit'],
                type='http',
                auth="public",
                website=True,
                methods=['POST'])
    def process_ticket(self, **kwargs):
        if not kwargs:
            return
        ticket_categ = None
        if int(kwargs.get('ticket_category')) > 0:
            ticket_categ = int(kwargs['ticket_category'])
        vals = {
            'ticket_subject': kwargs.get('ticket_subject'),
            'customer_name': kwargs.get('customer_name'),
            'email': kwargs.get('customer_email'),
            'description': kwargs.get('ticket_description'),
            'ticket_categ': ticket_categ
        }
        res = request.env['fsm.support.ticket'].sudo().create(
            vals
        )
        if res:
            return request.render("fs_support_ticket.ticket_create_success")
        else:
            return request.render("fs_support_ticket.ticket_create_error")
