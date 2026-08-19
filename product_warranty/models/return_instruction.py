# Copyright 2016 Cyril Gaudin (Camptocamp)
# Copyright 2015 Vauxoo
# Copyright 2009-2011  Akretion, Emmanuel Samyn, Benoît Guillot
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ReturnInstruction(models.Model):
    _name = "return.instruction"
    _description = "Instructions for product return"

    name = fields.Char("Title", required=True, translate=True)
    instructions = fields.Text(translate=True, help="Instructions for product return.")
    is_default = fields.Boolean(
        help="If is default, will be use "
        "to set the default value in "
        "supplier info's. Be careful to "
        "have only one default.",
    )
