from odoo import fields, models


class FSMPerson(models.Model):
    _inherit = "fsm.person"

    default_warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Default Warehouse",
        help="Default warehouse for this worker",
    )
