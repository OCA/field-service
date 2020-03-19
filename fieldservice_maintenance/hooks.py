# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
    # Check for existing fsm equipments
    cr.execute('SELECT * FROM fsm_equipment')
    equipments = []
    equipments = cr.dictfetchall()
    if equipments:
        # Add new columns to hold values
        cr.execute("""ALTER TABLE fsm_equipment
        ADD maintenance_equipment_id INT;""")
        cr.execute("""ALTER TABLE maintenance_equipment
        ADD is_fsm_equipment BOOLEAN;""")

        # Create a new Maintenance equipment for each FSM equipment
        for equipment in equipments:
            cr.execute("""INSERT INTO maintenance_equipment (
                name,
                equipment_assign_to,
                maintenance_team_id,
                is_fsm_equipment,
                effective_date,
                active)
            VALUES (
                %s,
                'other',
                1,
                True,
                %s,
                True);""", (
                equipment.get('name'),
                equipment.get('create_date'))
            )

            # Set this new Maintenance equipment on the existing FSM equipment
            cr.execute("""UPDATE fsm_equipment
                SET maintenance_equipment_id = (
                    SELECT id
                    FROM maintenance_equipment
                    ORDER BY id desc
                    LIMIT 1)
                WHERE id = %s;""",
                       (equipment.get('id'),))
