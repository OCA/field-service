import logging
from datetime import timedelta

from odoo import _, fields, http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

from ._booking import (
    PortalBookingError,
    dayroutes_with_available_capacity,
    get_dayroute,
    get_sale_template,
    get_service_type,
)

_logger = logging.getLogger(__name__)


class RequestsPortal(CustomerPortal):

    # ===== PORTAL HOME COUNTER =====
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'fsm_location_count' in counters:
            values['fsm_location_count'] = request.env['fsm.location'].sudo().search_count(
                self._requests_location_domain()
            )
        return values

    def _requests_location_domain(self):
        partner = request.env.user.partner_id.commercial_partner_id
        # Only locations that have equipment installed
        equipped_location_ids = request.env['fsm.equipment'].sudo().search(
            [('location_id', '!=', False)]
        ).mapped('location_id').ids
        return [
            ('owner_id', 'child_of', partner.id),
            ('id', 'in', equipped_location_ids),
        ]

    def _requests_check_location(self, location_id):
        """Return location if accessible and has equipment installed, else None."""
        location = request.env['fsm.location'].sudo().browse(location_id)
        if not location.exists():
            return None
        partner = request.env.user.partner_id.commercial_partner_id
        allowed_ids = partner.child_ids.ids + [partner.id]
        if not location.owner_id or location.owner_id.id not in allowed_ids:
            return None
        # Block access if no equipment installed on this location
        has_equipment = request.env['fsm.equipment'].sudo().search_count(
            [('location_id', '=', location_id)]
        )
        if not has_equipment:
            return None
        return location

    # ===== /my/requests — Location picker or redirect =====
    @http.route('/my/requests', type='http', auth='user', website=True)
    def portal_requests(self, **kw):
        locations = request.env['fsm.location'].sudo().search(
            self._requests_location_domain(), order='name asc'
        )
        if not locations:
            return request.render('fieldservice_portal.portal_requests_no_location', {
                'page_name': 'requests',
            })
        if len(locations) == 1:
            return request.redirect('/my/requests/%d' % locations[0].id)
        return request.render('fieldservice_portal.portal_requests_location_picker', {
            'locations': locations,
            'page_name': 'requests',
        })

    # ===== /my/requests/<id> — Location page =====
    @http.route('/my/requests/<int:location_id>', type='http', auth='user', website=True)
    def portal_requests_location(self, location_id, **kw):
        location = self._requests_check_location(location_id)
        if not location:
            return request.redirect('/my/requests')

        orders = request.env['fsm.order'].sudo().search([
            ('location_id', '=', location_id),
            ('stage_id.portal_visible', '=', True),
        ], order='request_early desc', limit=20)

        return request.render('fieldservice_portal.portal_requests_location', {
            'location': location,
            'orders': orders,
            'page_name': 'requests',
        })

    # ===== /my/requests/<id>/new — Slot booking form =====
    @http.route('/my/requests/<int:location_id>/new', type='http', auth='user', website=True)
    def portal_requests_new(self, location_id, **kw):
        location = self._requests_check_location(location_id)
        if not location:
            return request.redirect('/my/requests')
        return request.render('fieldservice_portal.portal_requests_new', {
            'location': location,
            'page_name': 'requests',
        })

    # ===== JSON: get available routes =====
    @http.route('/my/requests/routes', type='jsonrpc', auth='user', website=True)
    def requests_get_routes(self, **kw):
        try:
            today = fields.Date.context_today(request.env.user)
            end_date = today + timedelta(weeks=4)
            result = []
            for dr, remaining in dayroutes_with_available_capacity(
                'maintenance', end_date=end_date
            ):
                result.append({
                    'id': dr.id,
                    'date': str(dr.date),
                    'route_name': dr.route_id.name or '',
                    'person': dr.person_id.name or '',
                    'remaining': remaining,
                })
            return {'success': True, 'routes': result}
        except Exception:
            _logger.exception('Unable to load maintenance routes')
            return {
                'success': False,
                'error': _("Appointments are temporarily unavailable."),
            }

    # ===== JSON: submit maintenance request =====
    @http.route('/my/requests/submit', type='jsonrpc', auth='user', website=True)
    def requests_submit(self, **kw):
        try:
            location_id = int(kw.get('location_id', 0))
            description = kw.get('description', '')

            if not location_id:
                return {'success': False, 'error': _("No location specified")}

            location = self._requests_check_location(location_id)
            if not location:
                return {'success': False, 'error': _("Access denied")}

            partner = request.env.user.partner_id
            template = get_sale_template(
                'requests_sale_order_template_id', 'maintenance'
            )
            get_service_type('maintenance')
            dayroute = get_dayroute(kw.get('route_id'), 'maintenance', lock=True)

            with request.env.cr.savepoint():
                so = request.env['sale.order'].sudo().create({
                    'partner_id': partner.id,
                    'sale_order_template_id': template.id,
                    'fsm_location_id': location_id,
                    'portal_dayroute_id': dayroute.id,
                    'portal_service_description': description,
                    'company_id': request.env.company.id,
                })
                so._onchange_sale_order_template_id()
                so.validity_date = dayroute.date
                _logger.info(
                    'Maintenance quotation %s created for location %s',
                    so.name,
                    location_id,
                )
            return {
                'success': True,
                'sale_order_id': so.id,
                'redirect': '/my/orders/%d' % so.id,
            }
        except PortalBookingError as error:
            return {'success': False, 'error': error.args[0]}
        except (TypeError, ValueError):
            return {'success': False, 'error': _("The request details are invalid.")}
        except Exception:
            _logger.exception('Maintenance request failed')
            return {
                'success': False,
                'error': _("The request could not be created. Please try again."),
            }
