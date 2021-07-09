# Copyright (C) 2021, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(env, version):
    if not version:
        return

    env.execute("UPDATE fsm_order SET bill_to = 'location' " "WHERE bill_to IS NULL;")
