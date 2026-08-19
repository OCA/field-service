from odoo import fields, models


class ResDistrict(models.Model):
    _inherit = "res.district"

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        index=True,
    )
