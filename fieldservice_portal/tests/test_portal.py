import json

from odoo.tests.common import HttpCase, TransactionCase, new_test_user, tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestUsersHttp(HttpCase, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_portal = new_test_user(
            cls.env, login="portal", groups="base.group_portal"
        )
        cls.user_demo = new_test_user(
            cls.env, login="demouser", groups="base.group_user"
        )
        cls.portal_location = cls.env["fsm.location"].create(
            {
                "name": "Test Portal Location",
                "phone": "123",
                "email": "tpl@email.com",
                "partner_id": cls.user_portal.partner_id.id,
                "owner_id": cls.user_portal.partner_id.id,
            }
        )
        cls.test_order = cls.env["fsm.order"].create(
            {
                "name": "Demo Order",
                "description": "Description for the new demo order",
                "location_id": cls.portal_location.id,
            }
        )

    @mute_logger("odoo.http")
    def test_fsm_order_portal(self):
        # Accessing work order of the portal user through route APIs available
        self.authenticate(self.user_portal.login, self.user_portal.password)
        response = self.url_open("/my/fsm_orders")

        # Check successful response from API
        self.assertEqual(response.status_code, 200)

        self.authenticate(self.user_demo.login, self.user_demo.password)
        response = self.url_open("/my/fsm_orders")

        # Check Forbidden response from API
        self.assertEqual(response.status_code, 403)

    def test_fsm_order_access(self):
        order_id = self.env["fsm.order"].search([])[0].id
        self.authenticate(self.user_portal.login, self.user_portal.password)
        response = self.url_open("/my/fsm_order/" + str(order_id))
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
        expected_url = self.base_url() + "/my"
        self.authenticate(self.user_portal.login, self.user_portal.password)
        res = self.url_open("/my/fsm_order/" + str(order.id))
        self.assertEqual(res.url, expected_url)

    def test_fsm_order_kw_usage(self):
        order_id = self.env["fsm.order"].search([])[0].id
        # Trying to access fsm_order url
        # with query parameters
        self.authenticate(self.user_portal.login, self.user_portal.password)
        response = self.url_open(
            "/my/fsm_order/" + str(order_id) + "?success='success'"
        )
        self.assertEqual(response.status_code, 200)

    def test_fsm_no_fsm_order_present(self):
        # Trying to filter fsm_orders based on filter
        self.authenticate(self.user_portal.login, self.user_portal.password)
        response = self.url_open(
            "/my/fsm_orders?groupby=none&filterby=Completed&page=1&search_in=&search=",
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("<tbody>", response.text)
        self.assertIn("<p>There are no Work Orders in your account.</p>", response.text)

    def test_fsm_order_filter_usage(self):
        # Trying to filter fsm_orders based on filter, group and sort
        self.authenticate(self.user_portal.login, self.user_portal.password)
        response = self.url_open(
            "/my/fsm_orders?groupby=stage_id&filterby=New&sortby=location",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("<tbody>", response.text)
        self.assertIn("Demo Order", response.text)

    def test_fsm_orders_portal_home(self):
        self.authenticate(self.user_portal.login, self.user_portal.password)
        response = self.url_open("/my/home")
        self.assertEqual(response.status_code, 200)
        self.assertIn("FSM Orders", response.text)

    def test_fsm_orders_count(self):
        self.authenticate(self.user_portal.login, self.user_portal.password)
        response = self.url_open(
            "/my/counters",
            data=json.dumps({"params": {"counters": "fsm_order_count"}}).encode(),
            headers={"Content-Type": "application/json"},
        ).json()
        self.assertEqual(response["result"]["fsm_order_count"], 1)
