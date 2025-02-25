# models/fsm_order.py

from odoo import models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    def _get_or_create_tags(self, tag_names, product_tags):
        """Get existing tags or create missing ones."""
        FSMTag = self.env["fsm.tag"]
        existing_tags = FSMTag.search([("name", "in", tag_names)])
        missing_tags = product_tags.filtered(
            lambda tag: tag.name not in existing_tags.mapped("name")
        )
        new_tags = (
            FSMTag.create(
                [{"name": tag.name, "color": tag.color or 10} for tag in missing_tags]
            )
            if missing_tags
            else FSMTag
        )
        return existing_tags | new_tags

    def _sync_tags_from_products(self):
        for order in self:
            product_tags = order.move_ids.mapped("product_id.product_tmpl_id.tag_ids")
            tags = self._get_or_create_tags(product_tags.mapped("name"), product_tags)
            order.tag_ids = [(6, 0, tags.ids)]

    def _add_tags_for_product(self, product):
        for order in self:
            product_tags = product.product_tmpl_id.tag_ids
            tags = self._get_or_create_tags(product_tags.mapped("name"), product_tags)
            order.tag_ids |= tags
