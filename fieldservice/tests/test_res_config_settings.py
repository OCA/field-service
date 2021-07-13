from odoo.tests.common import TransactionCase


class TestSettings(TransactionCase):

    def test_module_purchase(self):

        config = self.env["res.config.settings"].create({})
        config._onchange_module_fieldservice_purchase()
        config.flush()
        config.execute()
        self.assertEqual(self.env.user.has_group('product.group_product_pricelist'), True)
