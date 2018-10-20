from odoo import http
from odoo.http import request


class SupportTicket(http.Controller):
    @http.route(['/fsm/ticket'], type='http', auth="public", website=True)
    def field_service_ticket(self, **kwargs):
        ticket_categ = request.env['fsm.ticket.category'].sudo().search([])
        customer_name = ''
        if request.env.user:
            if request.env.user.name != 'Public user':
                customer_name = request.env.user.name

        if request.env.user:
            email = request.env.user.partner_id.email
        else:
            email = ''
        values = {
            'ticket_categ': ticket_categ or [],
            'customer_name': customer_name,
            'email': email
        }

        return request.render("fsm_support_ticket.fs_tickets", values)

    @http.route(['/fsm/ticket/submit'],
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
            return request.render("fsm_support_ticket.ticket_create_success")
        else:
            return request.render("fsm_support_ticket.ticket_create_error")

    @http.route(['/fsm/tickets/list',
                 '/fsm/tickets/list/page/<int:page>'],
                type='http',
                auth="user",
                website=True)
    def list_tickets(self, page=1, **kwargs):
        user = request.env.user
        tickets_obj = request.env['fsm.support.ticket'].sudo()
        person_obj = request.env['fsm.person'].sudo()
        person = person_obj.search([
            ('partner_id', '=', user.partner_id.id)], limit=1)
        if person:
            domain = [
                '|',
                ('customer_id', '=', user.partner_id.id),
                ('person_id', '=', person.id)
            ]
        else:
            domain = [
                ('customer_id', '=', user.partner_id.id)
            ]
        tickets_count = tickets_obj.search(domain, count=True)

        # enabling pager for tickets
        # (in case there will be a large number of tickets)
        pager = request.website.pager(url='/fsm/tickets/list',
                                      total=tickets_count,
                                      page=page,
                                      step=30
                                      )
        tickets = tickets_obj.search(domain,
                                     offset=(page - 1) * 30,
                                     limit=30)

        states = tickets_obj.fields_get(allfields=['state'])

        return request.render("fsm_support_ticket.tickets_list", {
            'tickets': tickets,
            'pager': pager,
            'states': states['state']['selection']
        })
