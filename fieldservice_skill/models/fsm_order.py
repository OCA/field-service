# Copyright (C) 2018, Open Source Integrators
# Copyright (C) 2020, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    skill_ids = fields.Many2many("hr.skill", string="Required Skills")
    skill_worker_ids = fields.Many2many(
        "fsm.person",
        "fsm_order_skill_workers_rel",
        compute="_compute_skill_workers",
        help="Available workers based on skill requirements",
    )

    @api.onchange("category_ids")
    def _onchange_category_ids(self):
        if not self.template_id:
            skill_ids = []
            for category in self.category_ids:
                skill_ids.extend([skill.id for skill in category.skill_ids])
            self.skill_ids = [(6, 0, skill_ids)]

    @api.onchange("template_id")
    def _onchange_template_id(self):
        res = False
        if self.template_id:
            res = super(FSMOrder, self)._onchange_template_id()
            self.skill_ids = self.template_id.skill_ids
        return res

    @api.depends("skill_ids")
    def _compute_skill_workers(self):
        worker_ids = []
        req_skills = self.skill_ids.ids
        if not self.skill_ids:
            worker_ids = self.env["fsm.person"].search([]).ids
        else:
            FPS = self.env["fsm.person.skill"]
            potential_workers = FPS.search(
                [("skill_id", "in", self.skill_ids.ids)]
            ).mapped("person_id")
            for w in potential_workers:
                worker_skills = FPS.search([("person_id", "=", w.id)]).mapped(
                    "skill_id"
                )
                if set(worker_skills.ids) >= set(req_skills):
                    worker_ids.append(w.id)
        self.skill_worker_ids = [(6, 0, worker_ids)]
