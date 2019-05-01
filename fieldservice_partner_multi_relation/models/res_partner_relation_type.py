# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class ResPartnerRelationType(models.Model):
    _inherit = 'res.partner.relation.type'

    @api.multi
    def get_partner_types(self):
        super(ResPartnerRelationType, self).get_partner_types()
        return [
            ('c', _('Organisation')),
            ('p', _('Person')),
            ('fsm-location', _('FSM Location'))
        ]
