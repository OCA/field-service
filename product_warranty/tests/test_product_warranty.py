# Copyright 2016 Cyril Gaudin (Camptocamp)
# Copyright 2015 Vauxoo, Yanina Aular
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProductWarranty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.instruction_model = cls.env["return.instruction"]
        cls.supplierinfo = cls.env["product.supplierinfo"]
        cls.create_test_datas(cls)
        cls.create_product_supplierinfo(cls)

    def create_test_datas(self):
        """
        Create datas for test because not use demo datas.
        """
        self.return_instructions_id = self.env["return.instruction"].create(
            {
                "name": "Default Instruction",
                "instructions": (
                    "To return a product purchased through our platform vendor "
                    "Marketplace, access our online Returns Center and click "
                    "Return products to begin the application process for the return.\n"
                    "Select the product you want to return and the reason "
                    "for the return.You will need to provide detailed information "
                    "to enable the seller to handle your request. "
                    "Once the seller has reviewed your application, it will respond "
                    "by e-mail within 3 working days."
                ),
                "is_default": True,
            }
        )
        res_partner_main1 = self.env["res.partner"].create(
            {
                "name": "Chester Reed",
                "email": "ready.mat28@example.com",
                "function": "Chief Executive Officer (CEO)",
                "phone": "(803)-873-6126",
            }
        )
        self.env.company.crm_return_address_id = res_partner_main1

    def create_product_supplierinfo(self):
        """
        Create a record of product.supplier for next tests
        """

        product_tmpl_id = self.env["product.template"].create(
            {
                "name": "Desk Combination",
                "list_price": 450.0,
                "standard_price": 300.0,
                "type": "consu",
                "weight": 0.01,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "description_sale": "Desk combination, black-brown: "
                "chair + desk + drawer",
                "default_code": "FURN_7800",
            }
        )
        partner_id = self.env["res.partner"].create(
            {
                "name": "Ready Mat",
                "is_company": True,
                "street": "7500 W Linne Road",
                "city": "Tracy",
                "state_id": self.env.ref("base.state_us_5").id,
                "zip": "95304",
                "country_id": self.env.ref("base.us").id,
                "email": "ready.mat28@example.com",
                "phone": "(803)-873-6126",
                "website": "http://www.ready-mat.com/",
                "vat": "US12345675",
            }
        )

        other_partner = self.env["res.partner"].create(
            {
                "name": "Azure Interior",
                "is_company": True,
                "street": "4557 De Silva St",
                "city": "Fremont",
                "state_id": self.env.ref("base.state_us_5").id,
                "zip": "94538",
                "country_id": self.env.ref("base.us").id,
                "email": "azure.Interior24@example.com",
                "phone": "(870)-931-0505",
                "website": "http://www.azure-interior.com",
                "vat": "US12345677",
            }
        )

        supplierinfo_data = dict(
            partner_id=partner_id.id,
            product_name="Test SupplierInfo for display Default Instruction",
            min_qty=4,
            delay=5,
            warranty_return_partner="supplier",
            product_tmpl_id=product_tmpl_id.id,
            warranty_return_other_address=other_partner.id,
        )

        self.supplierinfo_brw = self.supplierinfo.create(supplierinfo_data)

    def test_default_instruction(self):
        """
        Test for return.instruction record with
        default field in True. If is assigned
        correctly when one record of
        product.supplierinfo is created
        """

        self.assertEqual(
            self.supplierinfo_brw.return_instructions.id, self.return_instructions_id.id
        )

    def test_return_instruction_content_is_translatable(self):
        self.assertTrue(self.return_instructions_id._fields["name"].translate)
        self.assertTrue(self.return_instructions_id._fields["instructions"].translate)

    def test_warranty_return_address(self):
        """
        Test warranty_return_address field is calculate correctly depends of
        warranty_return_partner
        """
        self.create_product_supplierinfo()

        self.assertEqual(
            self.supplierinfo_brw.warranty_return_address.id,
            self.supplierinfo_brw.partner_id.id,
        )

        self.supplierinfo_brw.write({"warranty_return_partner": "company"})

        self.assertEqual(
            self.supplierinfo_brw.warranty_return_address.id,
            self.supplierinfo_brw.company_id.crm_return_address_id.id,
        )

        self.supplierinfo_brw.write({"warranty_return_partner": "other"})

        self.assertEqual(
            self.supplierinfo_brw.warranty_return_address.id,
            self.supplierinfo_brw.warranty_return_other_address.id,
        )
