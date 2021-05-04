# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(env, version):
    if not version:
        return

    env.execute("""ALTER TABLE "fsm_location"
    ADD COLUMN IF NOT EXISTS "customer_id" INT;""")
    env.execute("""UPDATE "fsm_location" SET customer_id = owner_id
    WHERE customer_id IS NULL;""")
