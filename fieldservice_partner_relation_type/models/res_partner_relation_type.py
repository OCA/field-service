# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models

HANDLE_INVALID_ONCHANGE = [
    ('restrict',
     _('Do not allow change that will result in invalid relations')),
    ('ignore',
     _('Allow existing relations that do not fit changed conditions')),
    ('end',
     _('End relations per today, if they do not fit changed conditions')),
    ('delete',
     _('Delete relations that do not fit changed conditions')),
]


class ResPartnerRelationType(models.Model):
    _inherit = 'res.partner.relation.type'

    @api.multi
    def get_partner_types(self):
        super(ResPartnerRelationType, self)
        return [
            ('c', _('Organisation')),
            ('p', _('Person')),
            ('fsm-location', _('FSM Location'))
        ]
