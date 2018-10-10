# -*- coding: utf-8 -*-
import datetime
import logging
_logger = logging.getLogger(__name__)

from odoo.exceptions import UserError
from openerp import api, fields, models

class WebsiteSupportSLA(models.Model):

    _name = "website.support.sla"

    name = fields.Char(string="Name", translate=True)
    description = fields.Text(string="Description", translate=True)
    response_time_ids = fields.One2many('website.support.sla.response', 'vsa_id', string="Category Response Times (Working Hours)")
    alert_ids = fields.One2many('website.support.sla.alert', 'vsa_id', string="Email Alerts")

class WebsiteSupportSLAResponse(models.Model):

    _name = "website.support.sla.response"

    vsa_id = fields.Many2one('website.support.sla', string="SLA")
    category_id = fields.Many2one('website.support.ticket.categories', string="Ticket Category", required="True")
    response_time = fields.Float(string="Response Time", required="True")
    countdown_condition = fields.Selection([('business_only','Business Only'), ('24_hour','24 Hours')], default="24_hour", required="True")

    @api.multi
    def name_get(self):
        res = []
        for sla_response in self:
            name = sla_response.category_id.name + " (" + str(sla_response.response_time) + ")"
            res.append((sla_response, name))
        return res

    @api.model
    def create(self, values):
    
        #Can not have multiple of the same category on a single SLA
        if self.env['website.support.sla.response'].search_count([('vsa_id','=', values['vsa_id']), ('category_id','=', values['category_id'])]) > 0:
           raise UserError("You can not use the same category twice")
    
        #Setting for business hours has to be set before they can use business hours only SLA option
        if values['countdown_condition'] == 'business_only':
            setting_business_hours_id = self.env['ir.default'].get('website.support.settings', 'business_hours_id')
            if setting_business_hours_id is None:
                raise UserError("Please set business hours in settings before using this option")

        return super(WebsiteSupportSLAResponse, self).create(values)
        
class WebsiteSupportSLAAlert(models.Model):

    _name = "website.support.sla.alert"
    _order = "alert_time desc"

    vsa_id = fields.Many2one('website.support.sla', string="SLA")
    alert_time = fields.Float(string="Alert Time", help="Number of hours before or after SLA expiry to send alert")
    type = fields.Selection([('email','Email')], default="email", string="Type")