# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th)
# Copyright 2021 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestAgreement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.agreement_type = cls.env["agreement.type"].create(
            {
                "name": "Test Agreement Type",
                "domain": "purchase",
            }
        )
        cls.agreement = cls.env["agreement"].create(
            {
                "code": "TEST-AGREEMENT",
                "name": "Test agreement",
            }
        )

    def test_domain_selection(self):
        domain_agreement_type = self.env["agreement.type"]._domain_selection()
        domain_agreement = self.env["agreement"]._domain_selection()
        self.assertEqual(domain_agreement_type, domain_agreement)

    def test_human_readable_names_are_translatable(self):
        self.assertTrue(self.agreement._fields["name"].translate)
        self.assertTrue(self.agreement_type._fields["name"].translate)
        self.assertFalse(self.agreement._fields["code"].translate)

    def test_agreement_type_change(self):
        self.agreement.write({"agreement_type_id": self.agreement_type.id})
        self.assertEqual(self.agreement.domain, self.agreement_type.domain)

    def test_compute_display_name(self):
        display_name = self.agreement.display_name
        self.assertEqual(display_name, f"[{self.agreement.code}] {self.agreement.name}")

    def test_copy(self):
        agreement1 = self.agreement.copy(default={"code": "Test Code"})
        agreement2 = self.agreement.copy()
        self.assertEqual(agreement1.code, "Test Code")
        self.assertEqual(agreement2.code, f"{self.agreement.code} (copy)")
