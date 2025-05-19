import requests

from odoo.tests import common


class TestFieldserviceCrm(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        cls._super_send = requests.Session.send
        super().setUpClass()
        cls.location_1 = cls.env["fsm.location"].create(
            {
                "name": "Summer's House",
                "owner_id": cls.env["res.partner"]
                .create({"name": "Summer's Parents"})
                .id,
            }
        )

        cls.fsm_user = cls.env["res.users"].create(
            {
                "name": "Fsm User",
                "login": "fsm_user",
                "groups_id": [(6, 0, [cls.env.ref("fieldservice.group_fsm_user").id])],
            }
        )
        cls.lat = 48.8584
        cls.lon = 2.2945

    @classmethod
    def _request_handler(cls, s, r, /, **kw):
        """Don't block external requests."""
        return cls._super_send(s, r, **kw)

    def test_save_location_from_browser(self):
        fsm_order = self.env["fsm.order"].create(
            {
                "location_id": self.location_1.id,
            }
        )

        fsm_order.save_location_from_browser(self.lat, self.lon)

        self.assertEqual(fsm_order.location_id.city, "Paris")
        self.assertEqual(fsm_order.location_id.zip, "75007")

        fsm_order2 = self.env["fsm.order"].create(
            {
                "location_id": self.location_1.id,
            }
        )

        fsm_order2.save_location_from_browser(self.lat, self.lon)
        # No location will be created, because it's existing
        self.assertEqual(fsm_order2.location_id, fsm_order.location_id)
