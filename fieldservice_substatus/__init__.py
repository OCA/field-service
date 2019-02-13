# Copyright (C) 2019 - TODAY,  Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import models


def post_init_fsm(cr, registry):
    cr.execute("""UPDATE fsm_stage
        SET sub_stage_id = (SELECT id FROM fsm_stage_status LIMIT 1)
        WHERE sub_stage_id IS NULL""")
    cr.execute("""UPDATE fsm_order
        SET sub_stage_id = (SELECT id FROM fsm_stage_status LIMIT 1)
        WHERE sub_stage_id IS NULL""")
    cr.execute("""ALTER TABLE fsm_stage
        ALTER COLUMN sub_stage_id SET NOT NULL""")
    cr.execute("""ALTER TABLE fsm_order
        ALTER COLUMN sub_stage_id SET NOT NULL""")
    return True
