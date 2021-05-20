# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMPerson(models.Model):
    _name = "fsm.person"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread.blacklist"]
    _description = "Field Service Worker"

    partner_id = fields.Many2one(
        "res.partner",
        string="Related Partner",
        required=True,
        ondelete="restrict",
        delegate=True,
        auto_join=True,
    )
    category_ids = fields.Many2many("fsm.category", string="Categories")
    calendar_id = fields.Many2one("resource.calendar", string="Working Schedule")
    stage_id = fields.Many2one(
        "fsm.stage",
        string="Stage",
        index=True,
        copy=False,
        group_expand="_read_group_stage_ids",
        default=lambda self: self._default_stage_id(),
    )
    hide = fields.Boolean(default=False)
    mobile = fields.Char(string="Mobile")
    territory_ids = fields.Many2many("res.territory", string="Territories")

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        res = super(FSMPerson, self)._search(
            args=args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )
        # Check for args first having location_ids as default filter
        for arg in args:
            if isinstance(arg, (list)):
                if arg[0] == "location_ids":
                    # If given int search ID, else search name
                    if isinstance(arg[2], int):
                        self.env.cr.execute(
                            "SELECT person_id "
                            "FROM fsm_location_person "
                            "WHERE location_id=%s",
                            (arg[2],),
                        )
                    else:
                        arg[2] = "%" + arg[2] + "%"
                        self.env.cr.execute(
                            "SELECT id "
                            "FROM fsm_location "
                            "WHERE complete_name like %s",
                            (arg[2],),
                        )
                        location_ids = self.env.cr.fetchall()
                        if location_ids:
                            location_ids = [location[0] for location in location_ids]
                            self.env.cr.execute(
                                "SELECT DISTINCT person_id "
                                "FROM fsm_location_person "
                                "WHERE location_id in %s",
                                [tuple(location_ids)],
                            )
                    workers_ids = self.env.cr.fetchall()
                    if workers_ids:
                        preferred_workers_list = [worker[0] for worker in workers_ids]
                        return preferred_workers_list
        return res

    @api.model
    def create(self, vals):
        vals.update({"fsm_person": True})
        return super(FSMPerson, self).create(vals)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env["fsm.stage"].search([("stage_type", "=", "worker")])
        return stage_ids

    def _default_stage_id(self):
        return self.env["fsm.stage"].search(
            [("stage_type", "=", "worker"), ("sequence", "=", "1")]
        )

    def next_stage(self):
        seq = self.stage_id.sequence
        next_stage = self.env["fsm.stage"].search(
            [("stage_type", "=", "worker"), ("sequence", ">", seq)],
            order="sequence asc",
        )
        if next_stage:
            self.stage_id = next_stage[0]
            self._onchange_stage_id()

    def previous_stage(self):
        seq = self.stage_id.sequence
        prev_stage = self.env["fsm.stage"].search(
            [("stage_type", "=", "worker"), ("sequence", "<", seq)],
            order="sequence desc",
        )
        if prev_stage:
            self.stage_id = prev_stage[0]
            self._onchange_stage_id()

    @api.onchange("stage_id")
    def _onchange_stage_id(self):
        # get last stage
        heighest_stage = self.env["fsm.stage"].search(
            [("stage_type", "=", "worker")], order="sequence desc", limit=1
        )
        if self.stage_id.name == heighest_stage.name:
            self.hide = True
        else:
            self.hide = False
