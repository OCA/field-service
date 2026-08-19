from odoo import _, fields
from odoo.exceptions import UserError
from odoo.http import request


class PortalBookingError(UserError):
    pass


def dayroute_domain(route_type=None, end_date=None):
    domain = [
        ("date", ">=", fields.Date.context_today(request.env.user)),
        ("order_remaining", ">", 0),
        ("team_id.company_id", "=", request.env.company.id),
    ]
    if route_type:
        domain.append(("route_id.route_type", "=", route_type))
    if end_date:
        domain.append(("date", "<=", end_date))
    return domain


def dayroutes_with_available_capacity(route_type=None, end_date=None):
    dayroutes = request.env["fsm.route.dayroute"].sudo().search(
        dayroute_domain(route_type, end_date=end_date), order="date asc"
    )
    SaleOrder = request.env["sale.order"].sudo()
    available_dayroutes = []
    for dayroute in dayroutes:
        available = SaleOrder._portal_dayroute_available_capacity(dayroute)
        if available > 0:
            available_dayroutes.append((dayroute, available))
    return available_dayroutes


def get_dayroute(dayroute_id, route_type, needed_capacity=1, lock=False):
    try:
        dayroute_id = int(dayroute_id)
    except (TypeError, ValueError):
        raise PortalBookingError(_("Select a valid appointment.")) from None
    dayroute = request.env["fsm.route.dayroute"].sudo().search(
        [("id", "=", dayroute_id), *dayroute_domain(route_type)], limit=1
    )
    if not dayroute:
        raise PortalBookingError(_("The selected appointment is no longer available."))
    if lock:
        dayroute.lock_for_update()
        dayroute.invalidate_recordset(
            ["date", "order_remaining", "route_id", "team_id"]
        )
    if (
        dayroute.date < fields.Date.context_today(request.env.user)
        or dayroute.route_id.route_type != route_type
        or dayroute.team_id.company_id != request.env.company
    ):
        raise PortalBookingError(_("The selected appointment is no longer available."))
    available_capacity = request.env[
        "sale.order"
    ].sudo()._portal_dayroute_available_capacity(dayroute)
    if available_capacity < needed_capacity:
        raise PortalBookingError(_("The selected appointment has no remaining capacity."))
    return dayroute


def get_configured_record(model_name, company_field):
    record = request.env.company.sudo()[company_field]
    if record._name != model_name:
        raise PortalBookingError(_("This service is not configured yet."))
    return record.sudo().exists()


def get_service_type(service_type):
    order_type = request.env["fsm.order.type"].sudo().search(
        [("service_type", "=", service_type)], order="id", limit=1
    )
    if not order_type:
        raise PortalBookingError(_("This service is not configured yet."))
    return order_type


def get_sale_template(company_field, service_type):
    template = get_configured_record("sale.order.template", company_field)
    if (
        not template
        or template.service_type != service_type
        or (template.company_id and template.company_id != request.env.company)
        or not template.sale_order_template_line_ids
        or not template.sale_order_template_line_ids.filtered(
            lambda line: line.product_id.field_service_tracking != "no"
        )
    ):
        raise PortalBookingError(_("This service quotation is not configured yet."))
    return template


def get_crm_team(company_field="visit_crm_team_id"):
    team = get_configured_record("crm.team", company_field)
    if not team or (team.company_id and team.company_id != request.env.company):
        raise PortalBookingError(_("The site-survey team is not configured yet."))
    return team


def get_team_user(team):
    user = team.user_id.filtered(
        lambda candidate: not candidate.share
        and request.env.company in candidate.company_ids
    )
    if not user:
        user = request.env["res.users"].sudo().search(
            [
                ("sale_team_id", "=", team.id),
                ("share", "=", False),
                ("company_ids", "in", request.env.company.id),
            ],
            order="id",
            limit=1,
        )
    if not user:
        raise PortalBookingError(_("The site-survey team has no internal user."))
    return user


def district_domain():
    return [("company_id", "in", [request.env.company.id, False])]
