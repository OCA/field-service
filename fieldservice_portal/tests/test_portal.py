import json

from odoo.exceptions import AccessError
from odoo.http import Request
from odoo.tests.common import HttpCase, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestUsersHttp(HttpCase, TransactionCase):
    def test_fsm_order_portal(self):
        # Accessing work order of the portal user through route APIs available
        login = "portal"
        self.authenticate(login, login)
        response = self.url_open(
            "/my/fsm_orders",
            data={
                "validation": login,
                "password": login,
                "csrf_token": Request.csrf_token(self),
            },
        )

        # Check successful response from API
        self.assertEqual(response.status_code, 200)

        login = "demo"
        self.authenticate(login, login)
        response = self.url_open(
            "/my/fsm_orders",
            data={
                "validation": login,
                "password": login,
                "csrf_token": Request.csrf_token(self),
            },
        )

        # Check Forbidden response from API
        self.assertEqual(response.status_code, 403)

    def test_fsm_order_access(self):
        order_id = self.env["fsm.order"].search([])[0].id
        login = "portal"
        self.authenticate(login, login)
        response = self.url_open(
            "/my/fsm_order/" + str(order_id),
            data={
                "validation": login,
                "password": login,
                "csrf_token": Request.csrf_token(self),
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_fsm_order_access_denied(self):
        # create a Res Partner to be converted to FSM Location/Person
        test_loc_partner = self.env["res.partner"].create(
            {"name": "Test Loc Partner", "phone": "ABC", "email": "tlp@email.com"}
        )
        # create FSM Location and assign it to different user other than Portal User
        test_location = self.env["fsm.location"].create(
            {
                "name": "Test Location No Portal User",
                "phone": "123",
                "email": "tp@email.com",
                "customer_id": test_loc_partner.id,
                "partner_id": test_loc_partner.id,
                "owner_id": test_loc_partner.id,
            }
        )
        order = self.env["fsm.order"].create(
            {
                "location_id": test_location.id,
            }
        )

        # Trying to access fsm_order which is not
        # assigned to Portal User to check access error
        login = "portal"
        self.authenticate(login, login)
        self.url_open(
            "/my/fsm_order/" + str(order.id),
            data={
                "validation": login,
                "password": login,
                "csrf_token": Request.csrf_token(self),
            },
        )
        self.assertRaises(
            AccessError, msg="Access Denied by record rules for operation: read"
        )

    def test_fsm_order_kw_usage(self):
        order_id = self.env["fsm.order"].search([])[0].id
        # Trying to access fsm_order url
        # with query parameters
        login = "portal"
        self.authenticate(login, login)
        response = self.url_open(
            "/my/fsm_order/" + str(order_id) + "?success='success'",
            data={
                "validation": login,
                "password": login,
                "csrf_token": Request.csrf_token(self),
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_fsm_no_fsm_order_present(self):
        # Trying to filter fsm_orders based on filter
        login = "portal"
        self.authenticate(login, login)
        response = self.url_open(
            "/my/fsm_orders?groupby=none&filterby=Completed&page=1&search_in=&search=",
            data={
                "validation": login,
                "password": login,
                "csrf_token": Request.csrf_token(self),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("<tbody>", response.text)
        self.assertIn("<p>There are no Work Orders in your account.</p>", response.text)

    def test_fsm_order_filter_usage(self):
        # Trying to filter fsm_orders based on filter, group and sort
        login = "portal"
        self.authenticate(login, login)
        response = self.url_open(
            "/my/fsm_orders?groupby=stage_id&filterby=New&sortby=location",
            data={
                "validation": login,
                "password": login,
                "csrf_token": Request.csrf_token(self),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("<tbody>", response.text)
        self.assertIn("Demo Order", response.text)

    def test_fsm_orders_portal_home(self):
        login = "portal"
        self.authenticate(login, login)
        response = self.url_open(
            "/my/home",
            data={
                "validation": login,
                "password": login,
                "csrf_token": Request.csrf_token(self),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("FSM Orders", response.text)

    def test_fsm_orders_count(self):
        login = "portal"
        self.authenticate(login, login)
        response = self.url_open(
            "/my/counters",
            data=json.dumps(
                {
                    "validation": login,
                    "password": login,
                    "csrf_token": Request.csrf_token(self),
                    "params": {
                        "counters": "fsm_order_count",
                    },
                }
            ).encode(),
            headers={"Content-Type": "application/json"},
        ).json()
        self.assertEqual(response["result"]["fsm_order_count"], 1)
