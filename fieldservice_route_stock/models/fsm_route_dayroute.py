# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRouteDayRoute(models.Model):
    _inherit = 'fsm.route.dayroute'

    final_inventory_id = fields.Many2one(
        'stock.inventory', string='Final Inventory')

    @api.multi
    def write(self, vals):
        stage_obj = self.env['fsm.stage']
        accout_move_obj = self.env['account.move']
        # default inventory of all products so used all category
        product_categ = self.env.ref('product.product_category_all')
        for rec in self:
            journal_id = False
            amount = 0
            if vals.get('stage_id', False):
                account = (rec.fsm_vehicle_id.person_id.
                           property_account_receivable_id)
                partner = rec.fsm_vehicle_id.person_id.partner_id
                stage = stage_obj.browse(vals.get('stage_id'))
                if (stage.is_closed and stage.stage_type == 'route' and
                        rec.final_inventory_id.state == 'done'):
                    inventory_account = (
                        product_categ and
                        product_categ.property_stock_account_output_categ_id)
                    for move in rec.final_inventory_id.move_ids:
                        for acc_move in move.account_move_ids:
                            journal_id = acc_move.journal_id.id
                            for move_line in acc_move.line_ids:
                                amount += move_line.debit
                    if not journal_id:
                        journal_id = self.env['account.journal'].search(
                            [('type', '=', 'general'), ('code', '=', 'STJ')],
                            limit=1).id
                    move_line_debit_vals = {
                        'account_id': account.id,
                        'name': 'Inventory Adjustment',
                        'partner_id': partner.id,
                        'debit': amount,
                        'credit': 0,
                    }
                    move_line_credit_vals = {
                        'account_id': inventory_account.id,
                        'name': 'Inventory Adjustment',
                        'debit': 0,
                        'credit': amount,
                    }
                    move_vals = {
                        'journal_id': journal_id,
                        'line_ids': [(0, 0, move_line_debit_vals),
                                     (0, 0, move_line_credit_vals)]
                    }
                    move_id = accout_move_obj.create(move_vals)
                    rec.final_inventory_id.adjustment_move_id = move_id.id
        return super(FSMRouteDayRoute, self).write(vals)
