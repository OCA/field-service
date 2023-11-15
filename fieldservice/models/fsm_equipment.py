# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMEquipment(models.Model):
    _name = "fsm.equipment"
    _description = "Field Service Equipment"
    _inherit = ["mail.thread", "mail.activity.mixin", "fsm.model.mixin"]
    _stage_type = "equipment"

    name = fields.Char(required=True)
    person_id = fields.Many2one("fsm.person", string="Assigned Operator")
    location_id = fields.Many2one("fsm.location", string="Assigned Location")
    notes = fields.Text()
    territory_id = fields.Many2one("res.territory", string="Territory")
    branch_id = fields.Many2one("res.branch", string="Branch")
    district_id = fields.Many2one("res.district", string="District")
    region_id = fields.Many2one("res.region", string="Region")
    current_location_id = fields.Many2one("fsm.location", string="Current Location")
    managed_by_id = fields.Many2one("res.partner", string="Managed By")
    owned_by_id = fields.Many2one("res.partner", string="Owned By")
    parent_id = fields.Many2one("fsm.equipment", string="Parent")
    child_ids = fields.One2many("fsm.equipment", "parent_id", string="Children")
    color = fields.Integer("Color Index")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
        help="Company related to this equipment",
    )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Equipment name already exists!")
    ]

    @api.onchange("location_id")
    def _onchange_location_id(self):
        self.territory_id = self.location_id.territory_id

    @api.onchange("territory_id")
    def _onchange_territory_id(self):
        self.branch_id = self.territory_id.branch_id

    @api.onchange("branch_id")
    def _onchange_branch_id(self):
        self.district_id = self.branch_id.district_id

    @api.onchange("district_id")
    def _onchange_district_id(self):
        self.region_id = self.district_id.region_id
