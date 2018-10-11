# -*- coding: utf-8 -*-

from odoo import fields, models


class SupportTicketCategory(models.Model):
    _name = 'fsm.ticket.category'

    name = fields.Char(
        string="Name",
        required=True
    )
