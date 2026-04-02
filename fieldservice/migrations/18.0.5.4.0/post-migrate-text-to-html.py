# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api
from odoo.models import UPDATE_BATCH_SIZE
from odoo.tools import plaintext2html, split_every

_logger = logging.getLogger(__name__)


def _migrate_field_text_to_html(env, model, fname):
    """Migrate the field text to html"""
    _logger.info(f"Migrating {model}.{fname} Text->Html...")
    records = env[model].search([(fname, "!=", False)])
    for batch in split_every(UPDATE_BATCH_SIZE, records.ids, records.browse):
        for record in batch:
            setattr(record, fname, plaintext2html(getattr(record, fname, "")))
        batch.flush_recordset()


def migrate(cr, version):
    """Migrate the fsm.equipment.notes text field to html."""
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    _migrate_field_text_to_html(env, "fsm.equipment", "notes")
    _migrate_field_text_to_html(env, "fsm.order", "description")
    _migrate_field_text_to_html(env, "fsm.order", "resolution")
    _migrate_field_text_to_html(env, "fsm.location", "notes")
