# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMEquipment(models.Model):
    _name = "fsm.equipment"
    _description = "Field Service Equipment"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required="True")
    person_id = fields.Many2one("fsm.person", string="Assigned Operator")
    location_id = fields.Many2one("fsm.location", string="Assigned Location")
    notes = fields.Text(string="Notes")
    territory_id = fields.Many2one("res.territory", string="Territory")
    branch_id = fields.Many2one("res.branch", string="Branch")
    district_id = fields.Many2one("res.district", string="District")
    region_id = fields.Many2one("res.region", string="Region")
    current_location_id = fields.Many2one("fsm.location", string="Current Location")
    managed_by_id = fields.Many2one("res.partner", string="Managed By")
    owned_by_id = fields.Many2one("res.partner", string="Owned By")
    parent_id = fields.Many2one("fsm.equipment", string="Parent")
    child_ids = fields.One2many("fsm.equipment", "parent_id", string="Children")
    stage_id = fields.Many2one(
        "fsm.stage",
        string="Stage",
        track_visibility="onchange",
        index=True,
        copy=False,
        group_expand="_read_group_stage_ids",
        default=lambda self: self._default_stage_id(),
    )
    hide = fields.Boolean(default=False)
    color = fields.Integer("Color Index")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.user.company_id,
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

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env["fsm.stage"].search([("stage_type", "=", "equipment")])
        return stage_ids

    def _default_stage_id(self):
        return self.env["fsm.stage"].search(
            [("stage_type", "=", "equipment"), ("sequence", "=", "1")]
        )

    def next_stage(self):
        seq = self.stage_id.sequence
        next_stage = self.env["fsm.stage"].search(
            [("stage_type", "=", "equipment"), ("sequence", ">", seq)],
            order="sequence asc",
        )
        if next_stage:
            self.stage_id = next_stage[0]
            self._onchange_stage_id()

    def previous_stage(self):
        seq = self.stage_id.sequence
        prev_stage = self.env["fsm.stage"].search(
            [("stage_type", "=", "equipment"), ("sequence", "<", seq)],
            order="sequence desc",
        )
        if prev_stage:
            self.stage_id = prev_stage[0]
            self._onchange_stage_id()

    @api.onchange("stage_id")
    def _onchange_stage_id(self):
        # get last stage
        heighest_stage = self.env["fsm.stage"].search(
            [("stage_type", "=", "equipment")], order="sequence desc", limit=1
        )
        if self.stage_id.name == heighest_stage.name:
            self.hide = True
        else:
            self.hide = False
