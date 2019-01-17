# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError

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

    @api.multi
    def _check_partner(self, side):
        super(ResPartnerRelationType, self)
        for record in self:
            assert side in ['left', 'right']
            ptype = getattr(record.type_id, "contact_type_%s" % side)
            partner = getattr(record, '%s_partner_id' % side)
            if ((ptype == 'c' and not partner.is_company) or
                    (ptype == 'p' and partner.is_company) or
                    (ptype == 'fsm-location' and
                     not partner.fsm_location)):
                raise ValidationError(
                    _('The %s partner is not applicable for this '
                      'relation type.') % side
                )
            category = getattr(record.type_id, "partner_category_%s" % side)
            if category and category.id not in partner.category_id.ids:
                raise ValidationError(
                    _('The %s partner does not have category %s.') %
                    (side, category.name)
                )
