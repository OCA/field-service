# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    fsm_route_id = fields.Many2one(comodel_name="fsm.route", string="Route")
