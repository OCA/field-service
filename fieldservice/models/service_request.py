# Copyright 2017 Ursa Information Systems <http://www.ursainfosystems.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
# from odoo import api, _


class ServiceLocation(models.Model):
    _name = 'service.location'
    _description = 'Location of the service'

    # customer_id = fields.Many2one('res.partner', string='Customer')
    name = fields.Char(string='Name')
    location_type = fields.Char(string='Location Type', size=35)
    # building = fields.Char(string='Building', size=35)
    # floor = fields.Char(string='Floor', size=35)
    # longitude = fields.Float(string='Longitude')
    # latitude = fields.Float(string='Latitude')
    description = fields.Char(string='Description')
    # branch = fields.Char(string='Branch', size=35)
    # territory = fields.Char(string='Territory', size=35)
    # timezone = fields.Char(string='TimeZone', size=35)


class ServiceRequest(models.Model):
    _name = 'service.request'
    _description = 'Details of the Service Request'

    name = fields.Char(string='Name', required=True)
    route_id = fields.Many2one('routes')
    customer_id = fields.Many2one('res.partner', string='Customer')
    location = fields.Many2one('service.location', string='Location')
    field_service_person = fields.Many2one('field.service.person',
        string='Field Service Person')
    date = fields.Datetime(string='Scheduled Date')
    description = fields.Char(string='Description')
    stage = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('scheduled', 'Scheduled'),
        ('assigned', 'Assigned'),
        ('en_route', 'En Route'),
        ('started', 'Started'),
        ('complete', 'Complete'),
        ('cancelled', 'Cancelled')],
        default='new', string='Status', required=True)


class Activites(models.Model):
    _name = 'service.activities'
    _description = 'Create an Activity'

    service_request = fields.Many2one('service.request',
        string='Service Request')
    customer_id = fields.Many2one('res.partner', string='Customer')
    status = fields.Many2one('activity.status', string='Status')
    task = fields.Many2one('type.of.activity', string='Task')
    ticket = fields.Many2one('helpdesk.ticket', string='Ticket')
    # activity_type = fields.Many2one('type.of.activity', string='Type')
    name = fields.Char(string='Name', required=True)
    planned_duration = fields.Float(string='Planned Duration')
    # equipment = fields.One2many('equipment', string='Equipment')
    # assigned_to = fields.Many2one('', string='Assigned to')
    scheduled_start = fields.Datetime(string='Scheduled Start')
    scheduled_end = fields.Datetime(string='Scheduled End')
    actual_start = fields.Datetime(string='Actual Start')
    actual_end = fields.Datetime(string='Actual End')
    actual_duration = fields.Float(string='Actual Duration')
    priority = fields.Selection([
        ('0', 'Priority 0'),
        ('1', 'Priority 1'),
        ('2', 'Priority 2'),
        ('3', 'Priority 3'),
        ('4', 'Priority 4'),
        ('5', 'Priority 5')],
        string='Priority')
    sequence = fields.Integer(string='Sequence')
    signature_needed = fields.Boolean(string='Signature Needed')
    description = fields.Char(string='Descrition')
    # parts_needed = fields.Many2Many(string='Parts needed')


class Skill(models.Model):
    _name = 'skill'
    _description = 'Skill to be used later'

    name = fields.Char(string='Name', required=True)
    mandatory = fields.Boolean(string='Mandatory')
    description = fields.Char(string='Description')


class TerritoryPostal(models.Model):
    _name = 'territory.postal'
    _description = 'Postal code of a Territory'

    territory = fields.Char(string='Territory', size=35)
    postal_code = fields.Char(string='Postal Code', size=35)


class Territory(models.Model):
    _name = 'territory'
    _description = 'Territory info'

    name = fields.Char(string='Name', size=35, required=True)
    branch = fields.Char(string='Branch', size=35)
    postal_based = fields.Boolean(default=False,
        string='Postal-based', size=35, required=True)


class District(models.Model):
    _name = 'district'
    _description = 'District info'

    name = fields.Char(string='Name', size=35)
    region = fields.Char(string='Region', size=35)


class TypeOfServiceRequest(models.Model):
    _name = 'type.of.service.request'
    _description = 'Type of Service Request'

    # service_request_type =
    # description =


class TypeOfActivity(models.Model):
    _name = 'type.of.activity'
    _description = 'Type of Activity'
    
    # activity_type =
    # description =
    # default_parts_needed =


class Branch(models.Model):
    _name = 'branch'
    _description = 'Branch info'

    name = fields.Char(string='Name', size=35)
    district = fields.Char(string='District', size=35)


class PreferredAppointmentTimes(models.Model):
    _name = 'preferred.appointment.times'
    _description = 'Preferred appointment times'

    # service_request = fields.Many2one(string = 'Service Request')
    earliest_start = fields.Datetime(string='Earliest Start time and date')
    lastest_start = fields.Datetime(string='Latest Start time and date')


class ActivityStatus(models.Model):
    _name = 'activity.status'
    _description = 'Status of an Activity'

    description = fields.Char(string='ID', size=35)


class FieldServiePerson(models.Model):
    _name = 'field.service.person'
    _description = 'Workers who are deployed for Service Requests'

    name = fields.Char(string='Name', size=35, required=True)


class Routes(models.Model):
    _name = 'field.service.routes'
    _description = 'Routes made using a series of Service Requests'

    orders = fields.One2many('service.request', 'route_id',
        string='Service Requests')
    field_service_person = fields.Many2one('field.service.person',
        string='Field Service Person')
    date = fields.Date(string='Date')