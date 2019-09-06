# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FSMWizard(models.TransientModel):
    """
        A wizard to convert a res.partner record to a fsm.person or
         fsm.location
    """
    _inherit = 'fsm.wizard'

    def _prepare_fsm_location(self, partner):
        res = super(FSMWizard)._prepare_fsm_location(partner)
        res['owner_id'] = partner.id
        return res
