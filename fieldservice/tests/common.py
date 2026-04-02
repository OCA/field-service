# Copyright (C) 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Shared helpers for fieldservice tests (no demo data required)."""


def get_base_territory_test_records(env):
    """Return demo territory records, creating them when demo XML was not loaded."""
    territory = env.ref("base_territory.test_territory", raise_if_not_found=False)
    if territory:
        return {
            "test_region": env.ref("base_territory.test_region"),
            "test_district": env.ref("base_territory.test_district"),
            "test_branch": env.ref("base_territory.test_branch"),
            "test_territory": territory,
        }
    region = env["res.region"].create({"name": "Test Region"})
    district = env["res.district"].create(
        {"name": "Test District", "region_id": region.id}
    )
    branch = env["res.branch"].create(
        {"name": "Test Branch", "district_id": district.id}
    )
    territory = env["res.territory"].create(
        {"name": "Test Territory", "branch_id": branch.id}
    )
    return {
        "test_region": region,
        "test_district": district,
        "test_branch": branch,
        "test_territory": territory,
    }
