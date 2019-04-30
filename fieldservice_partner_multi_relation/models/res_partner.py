# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def get_partner_type(self):
        """
        Get partner type for relation.
        :return: 'c' for company or 'p' for person or
                 'fsm-location' for FSM Location
        :rtype: str
        """
        self.ensure_one()
        if self.fsm_location:
            return 'fsm-location'
        return super(ResPartner, self).get_partner_type()
