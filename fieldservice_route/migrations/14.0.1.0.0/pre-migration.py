# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(env, version):
    if not version:
        return

    index = 0
    for day in ('monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                'saturday', 'sunday'):
        env.execute("""UPDATE ir_model_data
        SET name='fsm_route_day_%s'
        WHERE name='fsm_route_day_%s' AND module='fieldservice_route';""" %
                    (index, day))
        index += 1
