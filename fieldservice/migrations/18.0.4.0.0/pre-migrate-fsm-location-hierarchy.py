from openupgradelib import openupgrade


def migrate(cr, version):
    """Rename fsm.location.fsm_parent_id to fsm.location.parent_id"""
    if not version:
        return

    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE fsm_location
        RENAME COLUMN fsm_parent_id TO parent_id;
        """,
    )
