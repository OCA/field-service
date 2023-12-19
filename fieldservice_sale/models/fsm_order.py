# Copyright (C) 2019 Brian McMaster
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    sale_id = fields.Many2one("sale.order")
    sale_line_id = fields.Many2one("sale.order.line")

    def action_view_sales(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [[False, "form"]],
            "res_id": self.sale_line_id.order_id.id or self.sale_id.id,
            "context": {"create": False},
            "name": _("Sales Orders"),
        }

    def message_post_with_view(self, views_or_xmlid, **kwargs):
        """Helper method to send a mail / post a message using a view_id to
        render using the ir.qweb engine. This method is stand alone, because
        there is nothing in template and composer that allows to handle
        views in batch. This method should probably disappear when templates
        handle ir ui views."""
        values = kwargs.pop("values", None) or dict()
        try:
            from odoo.addons.website.models.website import slug

            values["slug"] = slug
        except ImportError:
            values["slug"] = lambda self: self.id
        if isinstance(views_or_xmlid, str):
            views = self.env.ref("views_or_xmlid", raise_if_not_found=False)
        else:
            views = views_or_xmlid
        if not views:
            return
        for record in self:
            values["object"] = record
            rendered_template = views.render(values, engine="ir.qweb")
            kwargs["body"] = rendered_template
            record.message_post_with_template(False, **kwargs)
