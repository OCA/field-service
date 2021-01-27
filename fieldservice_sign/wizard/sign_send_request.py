# Copyright (C) 2021 Open Source Integrators
# Copyright (C) 2021 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class SignSendRequest(models.TransientModel):
    _inherit = "sign.send.request"

    fsm_order_id = fields.Many2one("fsm.order", "FSM Order")

    def send_request(self):
        res = super(SignSendRequest, self).send_request()
        request = self.env["sign.request"].browse(res.get("res_id"))
        request.fsm_order_id = self.fsm_order_id
        return res
