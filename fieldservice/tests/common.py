# Copyright 2025 Binhex
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from unittest.mock import patch

from odoo.addons.base_geolocalize.models.base_geocoder import GeoCoder

# Answer of the mocked geocoder, asserted where the test covers localization.
GEOCODER_COORDINATES = (50.123_456, 4.123_456)


class MockGeocoderCase:
    """Answer geocoding with a fixed point instead of the live service.

    Creating an fsm.location geolocalizes its partner when
    fieldservice_geoengine is installed, because its create() override calls
    geo_localize() with force_geo_localize. A test that creates a location would
    reach the live OpenStreetMap Nominatim service, and the framework blocks
    external requests.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.geocoder_patch = patch.object(
            GeoCoder, "_call_openstreetmap", side_effect=cls._geocode
        )
        cls.geocoder_patch.start()
        cls.addClassCleanup(cls.geocoder_patch.stop)

    @staticmethod
    def _geocode(addr, **kw):
        """Answer GEOCODER_COORDINATES, and nothing for an empty address."""
        return GEOCODER_COORDINATES if addr else None
