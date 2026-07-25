# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.exceptions import UserError
from odoo.tools.misc import file_open

from odoo.addons.fieldservice.tests.test_fsm_common import FSMCommon

TEST_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAACklEQVR4nGP4DwABAQEAGN2N9wAAAABJRU5ErkJggg=="  # noqa: E501


class TestFieldserviceSign(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.company
        cls.order = cls.env["fsm.order"].create({"location_id": cls.test_location.id})
        with file_open("sign_oca/tests/empty.pdf", "rb") as pdf_file:
            pdf_data = base64.b64encode(pdf_file.read())
        cls.sign_role = cls.env["sign.oca.role"].create(
            {
                "name": "FSM Test Customer",
                "partner_selection_policy": "expression",
                "expression_partner": "{{object.location_id.owner_id.id}}",
            }
        )
        cls.template = cls.env["sign.oca.template"].create(
            {
                "name": "FSM Order Test Template",
                "model_id": cls.env["ir.model"]._get_id("fsm.order"),
                "data": pdf_data,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "field_id": cls.env.ref("sign_oca.sign_field_signature").id,
                            "role_id": cls.sign_role.id,
                            "page": 1,
                            "position_x": 10,
                            "position_y": 10,
                            "width": 30,
                            "height": 4,
                            "required": True,
                        },
                    )
                ],
            }
        )
        cls.company.write(
            {
                "fsm_signature_capture": False,
                "fsm_document_signing": False,
                "fsm_require_signature_to_complete": False,
                "fsm_require_document_signed_to_complete": False,
                "fsm_order_sign_oca_template_id": False,
            }
        )

    def test_complete_without_guards(self):
        self.order.action_complete()
        self.assertEqual(
            self.order.stage_id,
            self.env.ref("fieldservice.fsm_stage_completed"),
        )

    def test_require_signature_to_complete(self):
        self.company.write(
            {
                "fsm_signature_capture": True,
                "fsm_require_signature_to_complete": True,
            }
        )
        with self.assertRaisesRegex(UserError, "Customer signature is required"):
            self.order.action_complete()
        self.order.write(
            {
                "signed_by": "Test Customer",
                "signature": TEST_IMAGE_BASE64,
            }
        )
        self.order.action_complete()
        self.assertEqual(
            self.order.stage_id,
            self.env.ref("fieldservice.fsm_stage_completed"),
        )

    def test_request_document_signature_disabled(self):
        with self.assertRaisesRegex(UserError, "Document signing is disabled"):
            self.order.action_request_document_signature()

    def test_request_document_signature_without_template(self):
        self.company.fsm_document_signing = True
        with self.assertRaisesRegex(UserError, "Configure an FSM Order Sign Template"):
            self.order.action_request_document_signature()

    def test_request_document_signature(self):
        self.company.write(
            {
                "fsm_document_signing": True,
                "fsm_order_sign_oca_template_id": self.template.id,
            }
        )
        action = self.order.action_request_document_signature()
        self.assertEqual(self.order.sign_request_count, 1)
        request = self.order.sign_request_id
        self.assertTrue(request)
        self.assertEqual(request.fsm_order_id, self.order)
        self.assertEqual(request.state, "0_sent")
        self.assertIn(
            self.test_location.owner_id,
            request.signer_ids.partner_id,
        )
        self.assertEqual(self.order.sign_request_state, "0_sent")
        self.assertEqual(
            action["domain"],
            [("id", "in", self.order.sign_request_ids.ids)],
        )

    def test_require_document_signed_to_complete(self):
        self.company.write(
            {
                "fsm_document_signing": True,
                "fsm_require_document_signed_to_complete": True,
                "fsm_order_sign_oca_template_id": self.template.id,
            }
        )
        self.order.action_request_document_signature()
        with self.assertRaisesRegex(UserError, "A signed document is required"):
            self.order.action_complete()
        self.order.sign_request_id.state = "2_signed"
        self.order.action_complete()
        self.assertEqual(
            self.order.stage_id,
            self.env.ref("fieldservice.fsm_stage_completed"),
        )

    def test_action_view_sign_requests(self):
        self.company.write(
            {
                "fsm_document_signing": True,
                "fsm_order_sign_oca_template_id": self.template.id,
            }
        )
        self.order.action_request_document_signature()
        action = self.order.action_view_sign_requests()
        self.assertEqual(
            action["domain"],
            [("id", "in", self.order.sign_request_ids.ids)],
        )
        self.assertEqual(
            action["context"]["default_record_ref"],
            f"fsm.order,{self.order.id}",
        )

    def test_compute_fsm_order_id_clears_non_order_refs(self):
        self.company.write(
            {
                "fsm_document_signing": True,
                "fsm_order_sign_oca_template_id": self.template.id,
            }
        )
        self.order.action_request_document_signature()
        request = self.order.sign_request_id
        self.assertEqual(request.fsm_order_id, self.order)
        partner = self.test_partner
        request.record_ref = f"{partner._name},{partner.id}"
        self.assertFalse(request.fsm_order_id)
