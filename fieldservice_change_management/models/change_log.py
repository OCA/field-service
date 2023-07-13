# Copyright (c) 2020 Pavlov Media <https://www.pavlovmedia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ChangeLog(models.Model):
    _name = "change.log"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "implemented_on desc"
    _description = "Change Log"

    active = fields.Boolean(default=True)
    name = fields.Char(string="Title", required=True)
    location_id = fields.Many2one("fsm.location", string="FSM Location")
    implemented_on = fields.Datetime(required=True, default=fields.Datetime.now)
    description = fields.Text(required=True)
    user_id = fields.Many2one(
        "res.users",
        string="Changed By",
        default=lambda self: self.env.user,
        tracking=True,
        required="1",
    )
    tag_ids = fields.Many2many("change.log.tag", string="Tags")
    type_id = fields.Many2one("change.log.type", string="Type", required=True)
    impact_id = fields.Many2one("change.log.impact", string="Impact", required=True)
    stage_id = fields.Many2one(
        "change.log.stage",
        string="Stage",
        group_expand="_read_group_stage_ids",
        default=lambda self: self.env.ref(
            "fieldservice_change_management.change_log_stage_active"
        )
        or 0,
        help="Select the current stage of the Bandwidth Change.",
    )
