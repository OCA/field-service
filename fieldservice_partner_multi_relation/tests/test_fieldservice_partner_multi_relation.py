# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.exceptions import ValidationError

from odoo.addons.partner_multi_relation.tests.test_partner_relation_common import (
    TestPartnerRelationCommon,
)


class TestPartnerRelation(TestPartnerRelationCommon):
    def setUp(self):
        super(TestPartnerRelation, self).setUp()

        self.fsm_location_01 = self.partner_model.create(
            {"name": "Test FSM Location - 1", "fsm_location": True, "ref": "FSM01"}
        )
        self.fsm_location_02 = self.partner_model.create(
            {"name": "Test FSM Location - 2", "fsm_location": True, "ref": "FSM02"}
        )
        self.fsm_company_03 = self.partner_model.create(
            {"name": "Test FSM Company - 2", "company_type": "", "ref": "FSM03"}
        )
        self.fsm_person_03 = self.partner_model.create(
            {"name": "Test FSM Person", "company_type": "person", "ref": "FSM04"}
        )
        self.fsm_location_obj = self.env["fsm.location"]
        # Create a new FSM > FSM relation type:
        (
            self.type_fsm_loc2fsm_loc,
            self.fsm_location2fsm_location,
            self.selection_fsm_loc3fsm_loc,
        ) = self._create_relation_type_selection(
            {
                "name": "FSM -> FSM",
                "name_inverse": "FSM <- FSM",
                "contact_type_left": "fsm-location",
                "contact_type_right": "fsm-location",
            }
        )

        # Create a new FSM > Person relation type:
        (
            self.type_fsm_loc2person,
            self.selection_fsm_loc2person,
            self.selection_person4fsm_loc,
        ) = self._create_relation_type_selection(
            {
                "name": "FSM -> Person",
                "name_inverse": "Person <- FSM",
                "contact_type_left": "fsm-location",
                "contact_type_right": "p",
            }
        )

        # Create a new FSM > Person relation type:
        (
            self.type_person2company,
            self.selection_person2company,
            self.selection_comapany2person,
        ) = self._create_relation_type_selection(
            {
                "name": "Person -> Company",
                "name_inverse": "Company <- Person",
                "contact_type_left": "c",
                "contact_type_right": "p",
            }
        )

    def test_validate_fsm_get_cat(self):
        relation = self.relation_all_model.new(
            {
                "this_partner_id": self.fsm_person_03.id,
                "type_selection_id": self.selection_person2company.id,
                "other_partner_id": self.fsm_company_03.id,
            }
        )
        relation.get_cat(self.fsm_person_03)
        relation.get_cat(self.fsm_company_03)

    def test_validate_fsm_location_01(self):
        self.fsm_location = self.fsm_location_obj.create(
            {
                "name": "Test FSM Location - 1",
                "owner_id": self.fsm_location_01.id,
            }
        )
        self.fsm_location._compute_relation_count()
        self.fsm_location.action_view_relations()

    def test_validate_fsm_location_02(self):
        """Test create overlapping with start / end dates."""
        self.fsm_location_01.get_partner_type()
        relation = self.relation_all_model.create(
            {
                "this_partner_id": self.fsm_location_01.id,
                "type_selection_id": self.fsm_location2fsm_location.id,
                "other_partner_id": self.fsm_location_02.id,
                "date_start": fields.Date.today(),
                "date_end": fields.Date.today(),
            }
        )
        relation.onchange_this_partner_id()
        relation.onchange_other_partner_id()
        relation.onchange_type_selection_id()
        # New relation with overlapping start / end should give error
        with self.assertRaises(ValidationError):
            self.relation_all_model.create(
                {
                    "this_partner_id": relation.this_partner_id.id,
                    "type_selection_id": relation.type_selection_id.id,
                    "other_partner_id": relation.other_partner_id.id,
                    "date_start": fields.Date.today(),
                    "date_end": fields.Date.today(),
                }
            )

    def test_validate_fsm_location_03(self):
        relation = self.relation_all_model.create(
            {
                "this_partner_id": self.partner_01_person.id,
                "type_selection_id": self.fsm_location2fsm_location.id,
                "other_partner_id": self.fsm_location_02.id,
            }
        )
        with self.assertRaises(ValidationError):
            relation.onchange_type_selection_id()

    def test_validate_fsm_location_04(self):
        relation = self.relation_all_model.create(
            {
                "this_partner_id": self.partner_02_company.id,
                "type_selection_id": self.selection_fsm_loc2person.id,
                "other_partner_id": self.fsm_location_02.id,
            }
        )
        with self.assertRaises(ValidationError):
            relation.onchange_type_selection_id()

    def test_validate_fsm_location_05(self):
        relation = self.relation_all_model.new(
            {
                "this_partner_id": self.partner_02_company.id,
                "type_selection_id": self.selection_fsm_loc2person.id,
                "other_partner_id": self.partner_01_person.id,
            }
        )
        with self.assertRaises(ValidationError):
            relation.onchange_type_selection_id()

    def test_validate_fsm_location_06(self):
        relation = self.relation_all_model.new(
            {
                "this_partner_id": self.fsm_location_01.id,
                "type_selection_id": self.fsm_location2fsm_location.id,
            }
        )
        relation.onchange_type_selection_id()
        relation.onchange_this_partner_id()

    def test_validate_fsm_location_07(self):
        relation = self.relation_all_model.new(
            {
                "other_partner_id": self.fsm_location_02.id,
                "type_selection_id": self.fsm_location2fsm_location.id,
            }
        )
        relation.onchange_type_selection_id()
        relation.onchange_other_partner_id()

    def test_validate_fsm_location_08(self):
        relation = self.relation_all_model.new(
            {
                "type_selection_id": self.fsm_location2fsm_location.id,
            }
        )
        relation.onchange_type_selection_id()

    def test_validate_fsm_location_09(self):
        relation = self.relation_all_model.new(
            {
                "this_partner_id": self.fsm_location_02.id,
            }
        )
        relation.onchange_this_partner_id()
        relation.onchange_type_selection_id()

    def test_validate_fsm_location_10(self):
        relation = self.relation_all_model.new(
            {
                "other_partner_id": self.fsm_location_01.id,
            }
        )
        relation.onchange_other_partner_id()
        relation.onchange_type_selection_id()

    def test_validate_fsm_location_11(self):
        relation = self.relation_all_model.new(
            {
                "this_partner_id": self.fsm_location_01.id,
                "other_partner_id": self.fsm_location_02.id,
            }
        )
        relation.onchange_this_partner_id()
        relation.onchange_other_partner_id()

    def test_validate_fsm_location_12(self):
        relation = self.relation_all_model.new(
            {
                "this_partner_id": self.fsm_person_03.id,
                "type_selection_id": self.selection_person2company.id,
            }
        )
        with self.assertRaises(ValidationError):
            relation.try_type()
            relation.onchange_this_partner_id()
            relation.onchange_other_partner_id()

    def test_validate_fsm_location_13(self):
        relation = self.relation_all_model.new(
            {
                "this_partner_id": self.fsm_person_03.id,
                "type_selection_id": self.selection_person2company.id,
                "other_partner_id": self.partner_02_company.id,
            }
        )
        relation.set_domain_left()
        relation.set_domain_right()

    def test_validate_fsm_location_14(self):
        relation = self.relation_all_model.new(
            {
                "this_partner_id": self.partner_02_company.id,
                "type_selection_id": self.selection_person2company.id,
                "other_partner_id": self.partner_02_company.id,
            }
        )
        relation.set_domain_left()
        relation.set_domain_right()
