# Copyright (C) 2021 Open Source Integrators
# Copyright (C) 2021 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import models
from odoo.exceptions import AccessError


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _fsm_check_attachment_access(self, mode, values=None):
        model_ids = defaultdict(set)
        if self:
            self.env["ir.attachment"].flush_model(
                ["res_model", "res_id", "public", "res_field"]
            )
            self.env.cr.execute(
                """SELECT res_model, res_id, create_uid, public, res_field
                  FROM ir_attachment WHERE id IN %s""",
                [tuple(self.ids)],
            )
            for (
                res_model,
                res_id,
                _create_uid,
                public,
                res_field,
            ) in self.env.cr.fetchall():
                if not self.env.is_system() and res_field:
                    raise AccessError(
                        self.env._(
                            "Sorry, you are not allowed to access this document."
                        )
                    )
                if public and mode == "read":
                    continue
                if not (res_model and res_id):
                    continue
                model_ids[res_model].add(res_id)
        if values and values.get("res_model") and values.get("res_id"):
            model_ids[values["res_model"]].add(values["res_id"])

        for res_model, res_ids in model_ids.items():
            if res_model not in self.env:
                continue
            if (
                res_model == "res.users"
                and len(res_ids) == 1
                and self.env.uid == list(res_ids)[0]
            ):
                continue
            records = self.env[res_model].browse(res_ids).exists()
            access_mode = "write" if mode in ("create", "unlink") else mode
            records._check_access(access_mode)

    def check(self, mode, values=None):
        """Restricts the access to an ir.attachment, according to referred mode."""
        if self.env.is_superuser():
            return True
        self._fsm_check_attachment_access(mode, values=values)
        return True
