from psycopg2.errors import UniqueViolation

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools.misc import mute_logger


class TestBlackoutDay(TransactionCase):
    @mute_logger("odoo.sql_db")
    def test_same_date_different_zip_allowed(self):
        self.env["fsm.blackout.day"].create(
            {
                "name": "ZIP 10001",
                "date": "2025-12-25",
                "zip": "10001",
            }
        )

        # Should not raise
        self.env["fsm.blackout.day"].create(
            {
                "name": "ZIP 90210",
                "date": "2025-12-25",
                "zip": "90210",
            }
        )

    @mute_logger("odoo.sql_db")
    def test_same_date_same_zip_not_allowed(self):
        self.env["fsm.blackout.day"].create(
            {
                "name": "First",
                "date": "2025-12-25",
                "zip": "10001",
            }
        )

        with self.assertRaises(UniqueViolation):
            self.env["fsm.blackout.day"].create(
                {
                    "name": "Duplicate",
                    "date": "2025-12-25",
                    "zip": "10001",
                }
            )

    @mute_logger("odoo.sql_db")
    def test_same_date_null_zip_not_allowed(self):
        self.env["fsm.blackout.day"].create(
            {
                "name": "Global Blackout 1",
                "date": "2025-12-25",
                "zip": False,
            }
        )

        with self.assertRaises(ValidationError):
            self.env["fsm.blackout.day"].create(
                {
                    "name": "Global Blackout 2",
                    "date": "2025-12-25",
                    "zip": False,
                }
            )
