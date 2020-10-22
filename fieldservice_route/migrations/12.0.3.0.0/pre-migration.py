# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(env, version):
    if not version:
        return

    env.execute("""ALTER TABLE fsm_route ADD max_dayroute INT;""")
    env.execute("""UPDATE fsm_route SET max_dayroute = 1;""")
