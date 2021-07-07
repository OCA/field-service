# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
    cr.execute("""ALTER TABLE "fsm_location" ADD "customer_id" INT;""")
    cr.execute(
        """UPDATE "fsm_location" SET customer_id = owner_id
    WHERE customer_id IS NULL;"""
    )
