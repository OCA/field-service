# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(env, version):
    if not version:
        return

    env.execute("UPDATE product_template SET field_service_tracking = 'sale' "
                "WHERE field_service_tracking = 'order';")
