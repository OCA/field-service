# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    warranty_start_date = fields.Date(
        copy=False, tracking=True, default=fields.Date.today
    )
    warranty_end_date = fields.Date(
        tracking=True, compute="_compute_warranty_end_date", store=True, readonly=False
    )
    product_warranty = fields.Integer(
        related="product_id.warranty", string="Warranty Duration"
    )
    product_warranty_type = fields.Selection(
        related="product_id.warranty_type", string="Warranty Type"
    )

    @api.constrains("warranty_start_date", "warranty_end_date")
    def _check_warranty_dates(self):
        for equip in self:
            if (
                equip.warranty_start_date
                and equip.warranty_end_date
                and equip.warranty_end_date < equip.warranty_start_date
            ):
                raise ValidationError(
                    self.env._("Warranty end date must be after warranty start date.")
                )

    def _get_warranty_end_date(self):
        self.ensure_one()
        warranty_end_date = fields.Date.today()
        if self.product_id and self.product_id.warranty:
            if self.product_id.warranty_type == "week":
                warranty_end_date = self.warranty_start_date + relativedelta(
                    weeks=self.product_id.warranty
                )
            elif self.product_id.warranty_type == "month":
                warranty_end_date = self.warranty_start_date + relativedelta(
                    months=self.product_id.warranty
                )
            elif self.product_id.warranty_type == "year":
                warranty_end_date = self.warranty_start_date + relativedelta(
                    years=self.product_id.warranty
                )
            else:
                warranty_end_date = fields.Date.today() + relativedelta(
                    days=self.product_id.warranty
                )
        return warranty_end_date

    @api.depends("product_id", "product_id.warranty", "warranty_start_date")
    def _compute_warranty_end_date(self):
        for equip in self:
            equip.warranty_end_date = equip._get_warranty_end_date()
