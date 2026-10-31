# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestFSMPersonWeb(HttpCase):
    def test_open_archived_worker(self):
        """An archived worker can be opened from the archived workers list"""
        worker = self.env["fsm.person"].create({"name": "Archived Worker"})
        worker.action_archive()
        self.authenticate("admin", "admin")
        res = self.make_jsonrpc_request(
            "/web/dataset/call_kw/fsm.person/web_read",
            {
                "model": "fsm.person",
                "method": "web_read",
                "args": [worker.ids],
                "kwargs": {"specification": {"name": {}, "active": {}}},
            },
        )
        self.assertEqual(res[0]["name"], "Archived Worker")
        self.assertFalse(res[0]["active"])
