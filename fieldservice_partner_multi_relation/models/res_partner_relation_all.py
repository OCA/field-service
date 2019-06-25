# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class ResPartnerRelationAll(models.AbstractModel):
    _inherit = 'res.partner.relation.all'

    @api.onchange('this_partner_id')
    def onchange_this_partner_id(self):
        if self.this_partner_id:
            type_id = self.env['res.partner.relation.type'].\
                search([('name', '=', self.type_selection_id.name)])
            if (type_id.contact_type_left == 'fsm-location'
                    or type_id.contact_type_right == 'fsm-location'
                    or self.this_partner_id.fsm_location
                    or self.other_partner_id.fsm_location):
                if not self.type_selection_id:
                    return self.set_domain_type()
            elif not self.this_partner_id:
                if not self.other_partner_id:
                    return {'domain': {'type_selection_id': ''}}

            else:
                super(ResPartnerRelationAll, self).onchange_partner_id()
        else:
            # Remove left_cat domain on type
            return self.set_domain_type()

    @api.onchange('other_partner_id')
    def onchange_other_partner_id(self):
        if self.other_partner_id:
            type_id = self.env['res.partner.relation.type'].\
                search([('name', '=', self.type_selection_id.name)])
            if (type_id.contact_type_left == 'fsm-location'
                    or type_id.contact_type_right == 'fsm-location'
                    or self.this_partner_id.fsm_location
                    or self.other_partner_id.fsm_location):
                if not type_id:
                    return self.set_domain_type()
                elif not self.other_partner_id:
                    if not self.this_partner_id:
                        return {'domain': {'type_selection_id': ''}}

            else:
                super(ResPartnerRelationAll, self).onchange_partner_id()
        else:
            # Remove right_cat domain on type
            self.set_domain_type()

    @api.onchange('type_selection_id')
    def onchange_type_selection_id(self):
        # Clear any prexisting domains
        if not self.type_selection_id:
            return {'domain':
                    {'this_partner_id': [('id', '!=', None)],
                     'other_partner_id': [('id', '!=', None)]}}
        type_id = self.env['res.partner.relation.type'].\
            search([('name', '=', self.type_selection_id.name)])
        if (type_id.contact_type_left == 'fsm-location'
                or type_id.contact_type_right == 'fsm-location'
                or self.this_partner_id.fsm_location
                or self.other_partner_id.fsm_location):
            if self.this_partner_id and self.other_partner_id:
                # Check
                self.try_type()
            elif self.this_partner_id:
                # Set domain Right
                res = self.set_domain_right()
                return res
            elif self.other_partner_id:
                # Set domain Left
                res = self.set_domain_left()
                return res
            else:
                res = self.set_domain_left()
                res2 = self.set_domain_right()
                res.update(res2['domain'])
                return res
        else:
            super(ResPartnerRelationAll, self).onchange_type_selection_id()

    def try_type(self):
        type_id = self.env['res.partner.relation.type'].\
            search([('name', '=', self.type_selection_id.name)])
        # From Type
        left_cat = type_id.contact_type_left
        right_cat = type_id.contact_type_right
        # Left Partner
        left_to_test = self.this_partner_id
        # Right Partner
        right_to_test = self.other_partner_id

        # Compare
        if left_cat == 'p':
            if left_to_test.company_type != 'person':
                raise ValidationError(_('Left Partner not type Person'))
        if left_cat == 'c':
            if left_to_test.company_type != 'compnay':
                raise ValidationError(_('Left Partner not type Company'))
        if left_cat == 'fsm-location':
            if not left_to_test.fsm_location:
                raise ValidationError(_('Left Partner not type FSM Location'))

        if right_cat == 'p':
            if right_to_test.company_type != 'person':
                raise ValidationError(_('Right Partner not type Person'))
        if right_cat == 'c':
            if right_to_test.company_type != 'compnay':
                raise ValidationError(_('Right Partner not type Company'))
        if right_cat == 'fsm-location':
            if not right_to_test.fsm_location:
                raise ValidationError(
                    _('Right Partner not type FSM Location'))

    def set_domain_left(self):
        type_id = self.env['res.partner.relation.type'].\
            search([('name', '=', self.type_selection_id.name)])
        # From Type
        res = {}
        # With a Relation Type
        if type_id:
            left_cat = type_id.contact_type_left
            # Create domain for Left based on Type Left Category
            res = self.build_domain(1, left_cat)
            return res
        # Without a Relation Type
        else:
            res = {'domain': {'this_partner_id': ''}}

    def set_domain_right(self):
        type_id = self.env['res.partner.relation.type'].\
            search([('name', '=', self.type_selection_id.name)])
        # From Type
        res = {}
        # With a Relation Type
        if type_id:
            right_cat = type_id.contact_type_right
            # Create domain for Right based on Type Right Category
            res = self.build_domain(0, right_cat)
            return res
        # Wtihout a Relation Type
        else:
            res = {'domain': {'other_partner_id': ''}}

    def set_domain_type(self):
        res = {}
        # If Left & Right then Type must match both
        if self.this_partner_id and self.other_partner_id:
            left_cat = self.get_cat(self.this_partner_id)
            right_cat = self.get_cat(self.other_partner_id)
            type_ids = self.env['res.partner.relation.type'].\
                search([('contact_type_left', '=', left_cat),
                        ('contact_type_right', '=', right_cat)])
            type_names = []
            for type_id in type_ids:
                type_names.append(type_id.name)
            # From Type
            res = {'domain':
                   {'type_selection_id': [('name', 'in', type_names)]}}
        # If Left Type must match Left
        elif self.this_partner_id:
            left_cat = self.get_cat(self.this_partner_id)
            type_ids = self.env['res.partner.relation.type'].\
                search([('contact_type_left', '=', left_cat)])
            type_names = []
            for type_id in type_ids:
                type_names.append(type_id.name)
            res = {'domain':
                   {'type_selection_id': [('name', 'in', type_names)]}}
        # If Right Type must match Right
        elif self.other_partner_id:
            right_cat = self.get_cat(self.other_partner_id)
            type_ids = self.env['res.partner.relation.type'].\
                search([('contact_type_right', '=', right_cat)])
            type_names = []
            for type_id in type_ids:
                type_names.append(type_id.name)
            res = {'domain':
                   {'type_selection_id': [('name', 'in', type_names)]}}
        return res

    def build_domain(self, side, cat):
        build = {}
        if cat == 'p':
            if side:
                build = {'domain':
                         {'this_partner_id':
                          [('company_type', '=', 'person')]}}
            else:
                build = {'domain':
                         {'other_partner_id':
                          [('company_type', '=', 'person')]}}
        if cat == 'c':
            if side:
                build = {'domain':
                         {'this_partner_id':
                          [('company_type', '=', 'company')]}}
            else:
                build = {'domain':
                         {'other_partner_id':
                          [('company_type', '=', 'company')]}}
        if cat == 'fsm-location':
            if side:
                build = {'domain':
                         {'this_partner_id': [('fsm_location', '=', True)]}}
            else:
                build = {'domain':
                         {'other_partner_id': [('fsm_location', '=', True)]}}
        return build

    def get_cat(self, partner):
        if partner.fsm_location:
            return 'fsm-location'
        elif partner.company_type == 'person':
            return 'p'
        else:
            return 'c'
