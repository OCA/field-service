# Copyright (C) 2022 Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(env, version):
    env.execute("UPDATE fsm_recurring SET state = 'close' WHERE state = 'cancel';")
    env.execute("UPDATE fsm_recurring SET state = 'progress' WHERE state = 'pending';")
