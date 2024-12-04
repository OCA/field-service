# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(env):
    env.cr.execute("""ALTER TABLE "fsm_location" ADD "customer_id" INT;""")
    env.cr.execute(
        """UPDATE "fsm_location" SET customer_id = owner_id
    WHERE customer_id IS NULL;"""
    )


def post_init_hook(env):
    group_analytic_accounting = env.ref(
        "analytic.group_analytic_accounting", raise_if_not_found=False
    )

    if group_analytic_accounting:
        users = env["res.users"].search([])

        for user in users:
            user.write({"groups_id": [(4, group_analytic_accounting.id)]})
