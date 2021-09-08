from openupgradelib import openupgrade

_column_renames = {
    "fsm_person_res_territory_rel": [("fsm_territory_id", "res_territory_id")]
}


def populate_res_territory(cr):
    openupgrade.logged_query(
        cr,
        """ALTER TABLE res_territory ADD COLUMN person_id INTEGER;
        """,
    )
    openupgrade.logged_query(
        cr,
        """INSERT INTO res_territory (id,name,branch_id,description,type,
        zip_codes,create_uid,create_date,write_uid,write_date,person_id)
        SELECT id,name,branch_id,description,type,zip_codes,create_uid,
        create_date,write_uid,write_date,person_id FROM fsm_territory""",
    )


def populate_res_region(cr):
    openupgrade.logged_query(
        cr, """INSERT INTO res_region SELECT * FROM fsm_region""")


def populate_res_district(cr):
    openupgrade.logged_query(
        cr, """INSERT INTO res_district SELECT * FROM fsm_district"""
    )


def populate_res_branch(cr):
    openupgrade.logged_query(cr, """INSERT INTO res_branch
        (id,name,partner_id,district_id,description,create_uid,
        create_date,write_uid,write_date) SELECT id,name,partner_id,
        district_id,description,create_uid,create_date,write_uid,write_date
        FROM fsm_branch""")


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    populate_res_region(cr)
    populate_res_district(cr)
    populate_res_branch(cr)
    populate_res_territory(cr)
    openupgrade.rename_tables(
        cr, [("fsm_person_fsm_territory_rel", "fsm_person_res_territory_rel")]
    )
    openupgrade.rename_columns(cr, _column_renames)
