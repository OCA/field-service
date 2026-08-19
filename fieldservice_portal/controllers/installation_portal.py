import logging
from datetime import timedelta

from odoo import _, fields, http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

from ._booking import (
    PortalBookingError,
    dayroutes_with_available_capacity,
    get_dayroute,
    get_service_type,
)

_logger = logging.getLogger(__name__)


class InstallationPortal(CustomerPortal):

    def _installation_check_sale_order(self, sale_order_id, require_ready=False):
        """Return sale order if accessible by current user, else None."""
        so = request.env['sale.order'].sudo().browse(sale_order_id)
        if not so.exists():
            return None
        partner = request.env.user.partner_id.commercial_partner_id
        so_partner = so.partner_id.commercial_partner_id
        if so_partner.id != partner.id:
            return None
        if so.company_id != request.env.company:
            return None
        if require_ready and (
            so._get_service_type() != 'installation'
            or not so.fsm_location_id
            or not so._is_installation_released()
        ):
            return None
        return so

    # ===== /my/installation/<id> — Slot picker page =====
    @http.route('/my/installation/<int:sale_order_id>', type='http', auth='user', website=True)
    def portal_installation(self, sale_order_id, **kw):
        so = self._installation_check_sale_order(sale_order_id, require_ready=True)
        if not so:
            return request.redirect('/my')
        return request.render('fieldservice_portal.portal_installation_slot_picker', {
            'so': so,
            'location': so.fsm_location_id,
            'page_name': 'installation',
        })

    # ===== JSON: get available installation routes =====
    @http.route('/my/installation/routes', type='jsonrpc', auth='user', website=True)
    def installation_get_routes(self, **kw):
        try:
            today = fields.Date.context_today(request.env.user)
            end_date = today + timedelta(weeks=4)
            result = []
            for dr, remaining in dayroutes_with_available_capacity(
                'installation', end_date=end_date
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
            _logger.exception('Unable to load installation routes')
            return {
                'success': False,
                'error': _("Appointments are temporarily unavailable."),
            }

    # ===== JSON: confirm installation slot =====
    @http.route('/my/installation/submit', type='jsonrpc', auth='user', website=True)
    def installation_submit(self, **kw):
        try:
            sale_order_id = int(kw.get('sale_order_id', 0))
            if not sale_order_id:
                return {'success': False, 'error': _("No sale order specified")}

            so = self._installation_check_sale_order(sale_order_id, require_ready=True)
            if not so:
                return {
                    'success': False,
                    'error': _("Sale order is not ready for installation"),
                }

            so.lock_for_update()
            so = self._installation_check_sale_order(sale_order_id, require_ready=True)
            if not so:
                raise PortalBookingError(_("Sale order is not ready for installation"))
            installation_type = get_service_type('installation')
            existing_orders = so.fsm_order_ids.sudo().sorted('id')
            if existing_orders:
                existing_orders.lock_for_update()
            scheduled_orders = existing_orders.filtered('dayroute_id')
            if scheduled_orders and len(scheduled_orders) != len(existing_orders):
                raise PortalBookingError(
                    _("The installation work orders are only partly scheduled.")
                )
            if scheduled_orders and len(scheduled_orders.mapped('dayroute_id')) != 1:
                raise PortalBookingError(
                    _("The installation work orders have conflicting appointments.")
                )
            if scheduled_orders:
                existing_order = scheduled_orders[0]
                return {
                    'success': True,
                    'order_id': existing_order.id,
                    'redirect': '/my/orders/%d' % so.id,
                }

            needed_capacity = len(existing_orders) or 1
            dayroute = get_dayroute(
                kw.get('route_id'),
                'installation',
                needed_capacity=needed_capacity,
                lock=True,
            )

            vals = {
                'location_id': so.fsm_location_id.id,
                'dayroute_id': dayroute.id,
                'person_id': dayroute.person_id.id,
                'team_id': dayroute.team_id.id,
                'request_early': dayroute.date_start_planned,
                'scheduled_date_start': dayroute.date_start_planned,
                'type': installation_type.id,
                'company_id': so.company_id.id,
            }
            if so.opportunity_id:
                vals['opportunity_id'] = so.opportunity_id.id

            with request.env.cr.savepoint():
                so.portal_dayroute_id = dayroute
                if existing_orders:
                    existing_orders.write(vals)
                    orders = existing_orders
                else:
                    orders = request.env['fsm.order'].sudo().create(
                        {**vals, 'sale_id': so.id}
                    )
                    _logger.info(
                        'Installation request %s created for SO %s',
                        orders.name,
                        so.name,
                    )

            return {
                'success': True,
                'order_id': orders[0].id,
                'redirect': '/my/orders/%d' % so.id,
            }

        except PortalBookingError as error:
            return {'success': False, 'error': error.args[0]}
        except (TypeError, ValueError):
            return {
                'success': False,
                'error': _("The installation details are invalid."),
            }
        except Exception:
            _logger.exception('Installation scheduling failed')
            return {
                'success': False,
                'error': _("The appointment could not be saved. Please try again."),
            }
