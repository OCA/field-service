# Copyright 2017 Ursa Information Systems <http://www.ursainfosystems.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

class ServiceLocation(models.Model):
    _name = 'service.location'
    _description = "Location of the service"

    owner = fields.Many2one('res.partner', string = 'Owner')
    # customer = fields.Many2one('', string = 'Customer')
    name = fields.Char(string = 'Name')
    location_type = fields.Char(string = 'Location Type', size = 35)
    building = fields.Char(string = 'Building', size = 35)
    floor = fields.Char(string = 'Floor', size = 35)
    longitude = fields.Float(string = 'Longitude')
    latitude = fields.Float(string = 'Latitude')
    description = fields.Char(string = 'Description')
    branch = fields.Char(string = 'Branch', size = 35)
    territory = fields.Char(string = 'Territory', size = 35)
    timezone = fields.Char(string = 'TimeZone', size = 35)

class ServiceRequest(models.Model):
    _name = 'service.request'

    request_type = fields.Many2one('service.request.type', string = 'Type Of Request')
    customer_id = fields.Many2one('res.partner', string = 'Customer')
    onsite_contact = fields.Many2one('res.partner', string = 'Onsite Contact')
    caller = fields.Many2one('res.parnter', string = 'Caller')
    status = fields.Selection([('new','New'), ('assigned', 'Assigned'), ('scheduled','Scheduled'), ('closed', 'Closed')], default = 'new', string = 'Status', required = True)
    equipment = fields.Many2one('equipment', string = 'Equipment')
    priority = fields.Selection([('1', 'Priority 1'), ('2', 'Priority 1'), ('3', 'Priority 3'), ('4', 'Priority 4'), ('5', 'Priority 5')], string = 'Priority', required = True)
    # service_location = fields.One2many('service.location', string = 'Service Location')
    # contract = fields.Many2one('contract', string = 'Contract')
    # quotation = fields.Many2one('sales', string = 'Quotation')
    po = fields.Many2one('purchase.order', string = 'PO')
    # maintenance_agreement = fields.Many2one('', string = 'Maintenance Agreement')
    creation_date = fields.Datetime(string = 'Creation date', required = True)
    completion_date = fields.Datetime(string = 'Completion date')
    # preferred_field_worker = fields.Many2one('', string = 'Preferred Field Worker')
    po_needed = fields.Boolean(string = 'PO Needed')
    # preferred_appointment_time = fields.Many2one('', string = 'Preferred Appointment times')

    # @api.model
    # def create(self, vals):
    #   Create stuff
    
    # @api.multi
    # def write(self, vals):
    #    Write Stuff

    # Delete Things

    # Redaction Things

class Activites(models.Model):
    _name = 'service.activities'

    service_request = fields.Many2one('service.request', string = 'Service Request')
    status = fields.Many2one('activity.status', string = 'Status')
    task = fields.Many2one('type.of.activity', string = 'Task')
    ticket = fields.Many2one('helpdesk.ticket', string = 'Ticket')
    # activity_type = fields.Many2one('type.of.activity', string = 'Type')
    name = fields.Char(string = 'Name', required = True)
    planned_druation = fields.Float(string = 'Planned Duration')
    # equipment = fields.One2many('equipment', string = 'Equipment')
    # assigned_to = fields.Many2one('', string = 'Assigned to')
    scheduled_start = fields.Datetime(string ='Scheduled Start')
    scheduled_end = fields.Datetime(string = 'Scheduled End')
    actual_start = fields.Datetime(string = 'Actual Start')
    actual_end = fields.Datetime(string = 'Actual End')
    actual_duration = fields.Float(string = 'Actual Duration')
    priority = fields.Selection([('0', 'Priority 0'), ('1', 'Priority 1'), ('2', 'Priority 1'), ('3', 'Priority 3'), ('4', 'Priority 4'), ('5', 'Priority 5')], string = 'Priority')
    sequence = fields.Integer(string = 'Sequence')
    signature_needed = fields.Boolean(string = 'Signature Needed')
    description = fields.Char(string = 'Descrition')
    # parts_needed = fields.Many2Many(string = 'Parts needed')



class Skill(models.Model):
    _name = 'skill'

    name = fields.Char(string = 'Name', required = True)
    mandatory = fields.Boolean(string = 'Mandatory')
    description = fields.Char(string = 'Description')

class TerritoryPostal(models.Model):
    _name = 'territory.postal'

    territory = fields.Char(string = 'Territory', size = 35)
    postal_code = fields.Char(string = 'Postal Code', size = 35)

class Territory(models.Model):
    _name = 'territory'

    name = fields.Char(string = 'Name', size = 35, required = True)
    branch = fields.Char(string = 'Branch', size = 35)
    postal_based = fields.Boolean(default = False, string = 'Postal-based', size = 35, required = True)

class District(models.Model):
    _name = 'district'

    name = fields.Char(string = 'Name', size = 35)
    region = fields.Char(string = 'Region', size = 35)

class TypeOfServiceRequest(models.Model):
    _name = 'type.of.service.request'

    # service_request_type = 
    # description =

class TypeOfActivity(models.Model):
    _name = 'type.of.activity'
    
    # activity_type =
    # description = 
    # default_parts_needed = 

class Branch(models.Model):
    _name = 'branch'

    name = fields.Char(string = 'Name', size = 35)
    district = fields.Char(string = 'District', size = 35)

class PreferredAppointmentTimes(models.Model):
    _name = 'preferred.appointment.times'

    # service_request = fields.Many2one(string = 'Service Request')
    earliest_start_time_date = fields.Datetime(string = 'Earliest Start time and date')
    lastest_start_time_and_date = fields.Datetime(string = 'Latest Start time and date')

class ActivityStatus(models.Model):
    _name = 'activity.status'

    description = fields.Char(string = 'ID', size = 35)