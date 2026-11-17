import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Detach the categories that are part of a recursive hierarchy.

    fsm.category becomes a _parent_store model, which cannot hold cycles.
    """
    if not version:
        return
    cr.execute(
        """
        WITH RECURSIVE ancestor(category_id, ancestor_id, path) AS (
            SELECT id, parent_id, ARRAY[id]
            FROM fsm_category
            WHERE parent_id IS NOT NULL
        UNION ALL
            SELECT anc.category_id, cat.parent_id, anc.path || cat.id
            FROM ancestor anc
            JOIN fsm_category cat ON cat.id = anc.ancestor_id
            WHERE cat.parent_id IS NOT NULL
                AND NOT cat.id = ANY(anc.path)
        )
        UPDATE fsm_category
        SET parent_id = NULL
        WHERE id IN (
            SELECT category_id FROM ancestor WHERE ancestor_id = category_id
        )
        RETURNING id, name
        """
    )
    for category_id, name in cr.fetchall():
        _logger.warning(
            "fsm.category %s (%s) was part of a recursive hierarchy: "
            "its parent has been removed.",
            category_id,
            name,
        )
