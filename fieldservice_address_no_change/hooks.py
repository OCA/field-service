# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def post_init_hook(env):
    fsm_orders = env["fsm.order"].search([])
    for order in fsm_orders:
        order.territory_id = order.location_id.territory_id or False
        order.branch_id = order.location_id.branch_id or False
        order.district_id = order.location_id.district_id or False
        order.region_id = order.location_id.region_id or False
        order.street = order.location_id.street
        order.street2 = order.location_id.street2
        order.zip = order.location_id.zip
        order.city = order.location_id.city
        order.state_name = order.location_id.state_id.name or False
        order.country_name = order.location_id.country_id.name or False
