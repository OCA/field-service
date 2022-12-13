# Copyright 2022 Rafnix Guzman
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    labels_logo = fields.Image("Labels logo", max_width=512, max_height=512)
