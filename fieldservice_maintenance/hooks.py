# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(env):
    # Check for existing fsm equipments
    env.cr.execute("SELECT * FROM fsm_equipment")
    equipments = []
    equipments = env.cr.dictfetchall()
    if equipments:
        # Add new columns to hold values
        env.cr.execute(
            """ALTER TABLE fsm_equipment
        ADD maintenance_equipment_id INT;"""
        )
        env.cr.execute(
            """ALTER TABLE maintenance_equipment
        ADD is_fsm_equipment BOOLEAN;"""
        )

        # Create a new Maintenance equipment for each FSM equipment
        for equipment in equipments:
            env.cr.execute(
                """INSERT INTO maintenance_equipment (
                name,
                maintenance_team_id,
                is_fsm_equipment,
                effective_date,
                active)
            VALUES (
                %s,
                1,
                True,
                %s,
                True);""",
                (equipment.get("name"), equipment.get("create_date")),
            )

            # Set this new Maintenance equipment on the existing FSM equipment
            env.cr.execute(
                """UPDATE fsm_equipment
                SET maintenance_equipment_id = (
                    SELECT id
                    FROM maintenance_equipment
                    ORDER BY id desc
                    LIMIT 1)
                WHERE id = %s;""",
                (equipment.get("id"),),
            )
