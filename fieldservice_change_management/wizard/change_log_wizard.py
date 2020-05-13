# Copyright (c) 2020 Pavlov Media <https://www.pavlovmedia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ChangeLogWizard(models.TransientModel):
    """A wizard to create change logs on multiple fsm locations"""
    _name = 'change.log.wizard'
    _description = 'Change Log Wizard'

    fsm_location_ids = fields.One2many('fsm.location', string="Locations")
    name = fields.Char(string="Title", required=True)
    implemented_on = fields.Datetime(string="Implemented On", required=True,
                                     default=fields.Datetime.now)
    description = fields.Text(string="Description", required=True)
    user_id = fields.Many2one('res.users', string="Changed By",
                              default=lambda self: self.env.user,
                              track_visibility="onchange",
                              required="1")
    type_id = fields.Many2one('change.log.type', string="Type", required=True)
    impact_id = fields.Many2one('change.log.impact', string="Impact",
                                required=True)
