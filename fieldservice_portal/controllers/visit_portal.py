import logging
from datetime import timedelta

from odoo import _, fields, http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

from ._booking import (
    PortalBookingError,
    dayroutes_with_available_capacity,
    district_domain,
    get_crm_team,
    get_dayroute,
    get_sale_template,
    get_service_type,
    get_team_user,
)

_logger = logging.getLogger(__name__)


class VisitPortal(CustomerPortal):

    @http.route('/my/visit', type='http', auth='user', website=True)
    def portal_request_visit(self, **kw):
        """2-step site visit booking: 1) Location  2) Appointment"""
        partner = request.env.user.partner_id
        company = request.env.company
        company_partner = company.partner_id
        maps_key = request.website.google_maps_api_key
        states = request.env['res.country.state'].sudo().search(
            [('country_id', '=', company.country_id.id)], order='name'
        )
        regions = request.env['res.region'].sudo().search(
            [('state_id', 'in', states.ids)], order='name'
        )
        districts = request.env['res.district'].sudo().search(
            [('region_id', 'in', regions.ids)], order='name'
        )
        values = {
            'partner': partner,
            'page_name': 'visit',
            'map_country_code': company.country_id.code or 'EG',
            'map_city': company.city or 'Cairo',
            'map_latitude': company_partner.partner_latitude or 30.0444,
            'map_longitude': company_partner.partner_longitude or 31.2357,
            'map_language': (request.env.lang or 'en_US').split('_')[0],
            'visit_confirmation_policy': company.visit_confirmation_policy,
            'states': states,
            'regions': regions,
            'districts': districts,
            'manual_location': not bool(maps_key),
        }
        return request.render('fieldservice_portal.portal_visit_form', values)

    @http.route('/available-routes', type='jsonrpc', auth='user', methods=['POST'])
    def get_available_dayroutes(self, **kw):
        """Return company day routes with available capacity."""
        try:
            result = []
            for dr, remaining in dayroutes_with_available_capacity():
                result.append({
                    'id': dr.id,
                    'name': dr.name,
                    'date': dr.date.isoformat() if dr.date else None,
                    'person_id': dr.person_id.id if dr.person_id else None,
                    'person_name': dr.person_id.name if dr.person_id else None,
                    'route_id': dr.route_id.id if dr.route_id else None,
                    'route_name': dr.route_id.name if dr.route_id else None,
                    'order_count': dr.order_count,
                    'max_order': dr.max_order,
                    'order_remaining': remaining,
                    'stage_id': dr.stage_id.id if dr.stage_id else None,
                    'stage_name': dr.stage_id.name if dr.stage_id else None,
                })
            return {'status': 'success', 'count': len(result), 'dayroutes': result}
        except Exception:
            _logger.exception("Unable to load available routes")
            return {
                'status': 'error',
                'message': _("Appointments are temporarily unavailable."),
            }

    @http.route('/my/visit/routes', type='jsonrpc', auth='user', website=True)
    def get_available_routes(self, **kw):
        """Get available dayroutes for the next 4 weeks"""
        try:
            today = fields.Date.context_today(request.env.user)
            end_date = today + timedelta(weeks=4)
            result = []
            for dr, remaining in dayroutes_with_available_capacity(
                'visit', end_date=end_date
            ):
                result.append({
                    'id': dr.id,
                    'name': dr.name or '',
                    'date': str(dr.date) if dr.date else '',
                    'route_name': dr.route_id.name or '',
                    'person': dr.person_id.name or '',
                    'remaining': remaining,
                    'max_order': dr.max_order,
                })
            return {'success': True, 'routes': result}
        except Exception:
            _logger.exception("Unable to load visit routes")
            return {
                'success': False,
                'error': _("Appointments are temporarily unavailable."),
            }

    @http.route('/my/visit/districts', type='jsonrpc', auth='user', methods=['POST'])
    def get_district_polygons(self, **kw):
        """Return company districts used by the coverage map."""
        try:
            districts = request.env['res.district'].sudo().search(district_domain())
            result = []
            for d in districts:
                result.append({
                    'id': d.id,
                    'name': d.name,
                    'polygon': [{'lat': p.lat, 'lng': p.lng} for p in d.polygon_ids],
                })
            return {'status': 'success', 'districts': result}
        except Exception:
            _logger.exception("Unable to load service districts")
            return {
                'status': 'error',
                'message': _("Coverage information is temporarily unavailable."),
            }

    @http.route('/my/visit/submit', type='jsonrpc', auth='user', website=True)
    def submit_visit_request(self, **kw):
        """Submit the visit booking as a CRM lead"""
        try:
            partner = request.env.user.partner_id
            visit_team = get_crm_team()
            template = get_sale_template(
                'visit_sale_order_template_id', 'survey'
            )
            get_service_type('survey')
            dayroute = get_dayroute(kw.get('route_id'), 'visit', lock=True)

            country = request.env.company.country_id.sudo()
            if not country:
                raise PortalBookingError(_("The company country is not configured."))
            if kw.get('country_code') and kw['country_code'].upper() != country.code:
                raise PortalBookingError(_("Select a valid country."))

            manual_requested = kw.get('manual_location') in (True, 1, '1', 'true')
            latitude = longitude = None
            if not manual_requested and kw.get('latitude') and kw.get('longitude'):
                try:
                    latitude = float(kw['latitude'])
                    longitude = float(kw['longitude'])
                except (TypeError, ValueError):
                    raise PortalBookingError(_("Select a valid location.")) from None
                if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                    raise PortalBookingError(_("Select a valid location."))
            manual_location = latitude is None or longitude is None

            visit_user = get_team_user(visit_team)

            vals = {
                'name': request.env._("New site survey booking"),
                'partner_id': partner.id,
                'phone': partner.phone or partner.mobile or '',
                'user_id': visit_user.id,
                'team_id': visit_team.id,
            }

            # Location fields
            if latitude is not None:
                vals['partner_latitude'] = latitude
            if longitude is not None:
                vals['partner_longitude'] = longitude
            if kw.get('street'):
                vals['street'] = kw['street']
            if kw.get('unit'):
                vals['street2'] = kw['unit']
            if kw.get('city'):
                vals['city'] = kw['city']
            if kw.get('zip'):
                vals['zip'] = kw['zip']

            state = request.env['res.country.state']
            if kw.get('state_id'):
                try:
                    state_id = int(kw['state_id'])
                except (TypeError, ValueError):
                    raise PortalBookingError(_("Select a valid state.")) from None
                state = request.env['res.country.state'].sudo().search(
                    [('id', '=', state_id), ('country_id', '=', country.id)], limit=1
                )
                if not state:
                    raise PortalBookingError(_("Select a valid state."))

            region = request.env['res.region']
            if kw.get('region_id'):
                try:
                    region_id = int(kw['region_id'])
                except (TypeError, ValueError):
                    raise PortalBookingError(_("Select a valid region.")) from None
                region = request.env['res.region'].sudo().search(
                    [('id', '=', region_id), ('state_id', '=', state.id)], limit=1
                )
                if not region:
                    raise PortalBookingError(_("Select a valid region."))

            manual_region = str(kw.get('manual_region') or '').strip()
            city = str(kw.get('city') or '').strip()
            street = str(kw.get('street') or '').strip()
            unit = str(kw.get('unit') or '').strip()
            if not street or not unit or (
                manual_location and (
                    not state or not (region or manual_region) or not city
                )
            ):
                raise PortalBookingError(
                    _("Enter the state, region, city, street, and building number.")
                )

            district = request.env['res.district']
            if kw.get('district_id'):
                try:
                    district_id = int(kw['district_id'])
                except (TypeError, ValueError):
                    raise PortalBookingError(
                        _("Select a valid service district.")
                    ) from None
                district = request.env['res.district'].sudo().search(
                    [('id', '=', district_id), *district_domain()], limit=1
                )
                if not district or (region and district.region_id != region):
                    raise PortalBookingError(_("Select a valid service district."))
            if manual_location and not district:
                raise PortalBookingError(_("Select a valid service district."))
            is_outside_coverage = not district
            if is_outside_coverage:
                vals['name'] += request.env._(" (outside coverage)")

            # Dayroute info stored in description
            description = request.env._(
                "Visit appointment: %(date)s - %(route)s",
                date=dayroute.date,
                route=dayroute.route_id.name or dayroute.name,
            )

            if is_outside_coverage:
                description += request.env._(
                    "\n[Notice: This location is outside automatic coverage. "
                    "Please review it and contact the customer manually.]"
                )

            vals['description'] = description

            if district:
                vals['district_id'] = district.id
            if state:
                vals['state_id'] = state.id
            if region:
                vals['region_id'] = region.id
            vals['country_id'] = country.id

            # Create a dedicated child partner for this location's address
            # (fsm.location uses _inherits on res.partner, so writing address
            # fields to the location would overwrite the main partner's address)
            location_partner_vals = {
                'name': partner.name,
                'type': 'other',
                'parent_id': partner.id,
            }
            if latitude is not None:
                location_partner_vals['partner_latitude'] = latitude
            if longitude is not None:
                location_partner_vals['partner_longitude'] = longitude
            if kw.get('street'):
                location_partner_vals['street'] = kw['street']
            if kw.get('unit'):
                location_partner_vals['street2'] = kw['unit']
            if kw.get('city'):
                location_partner_vals['city'] = kw['city']
            if kw.get('zip'):
                location_partner_vals['zip'] = kw['zip']
            if district:
                location_partner_vals['district_id'] = district.id
            if state:
                location_partner_vals['state_id'] = state.id
            if region:
                location_partner_vals['region_id'] = region.id
            location_partner_vals['country_id'] = country.id

            with request.env.cr.savepoint():
                lead = request.env['crm.lead'].sudo().create(vals)
                location_partner = request.env['res.partner'].sudo().create(
                    location_partner_vals
                )
                location = request.env['fsm.location'].sudo().create({
                    'partner_id': location_partner.id,
                    'owner_id': partner.id,
                    'shipping_address_id': partner.id,
                })
                lead.write({
                    'name': request.env._(
                        "New site survey for %(partner)s", partner=partner.name or ""
                    ),
                    'fsm_location_id': location.id,
                })
                so = request.env['sale.order'].sudo().create({
                    'partner_id': partner.id,
                    'user_id': visit_user.id,
                    'team_id': visit_team.id,
                    'opportunity_id': lead.id,
                    'fsm_location_id': location.id,
                    'sale_order_template_id': template.id,
                    'portal_dayroute_id': dayroute.id,
                    'company_id': request.env.company.id,
                })
                so._onchange_sale_order_template_id()
                so.validity_date = dayroute.date
                _logger.info(
                    "Visit booking %s created for partner %s", lead.id, partner.id
                )

            return {
                'success': True,
                'lead_id': lead.id,
                'redirect': '/my/orders/%d' % so.id,
            }
        except PortalBookingError as error:
            return {'success': False, 'error': error.args[0]}
        except (TypeError, ValueError):
            return {'success': False, 'error': _("The booking details are invalid.")}
        except Exception:
            _logger.exception("Visit booking failed")
            return {
                'success': False,
                'error': _("The booking could not be created. Please try again."),
            }
