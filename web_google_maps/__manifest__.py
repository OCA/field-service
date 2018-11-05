# -*- coding: utf-8 -*-
{
    'name': 'Web Google Maps',
    'version': '11.0.1.0.5',
    'author': 'Yopi Angi',
    'license': 'AGPL-3',
    'maintainer': 'Yopi Angi<yopiangi@gmail.com>',
    'support': 'yopiangi@gmail.com',
    'category': 'Extra Tools',
    'description': """
Web Google Map and google places autocomplete address form
==========================================================

This module brings three features:
1. Allows user to view all partners addresses on google maps.
2. Enabled google places autocomplete address form into partner
form view, it provide autocomplete feature when typing address of partner
""",
    'depends': [
        'base_setup',
        'base_geolocalize',
    ],
    'website': '',
    'data': [
        'data/google_maps_libraries.xml',
        'views/google_places_template.xml',
        'views/res_partner.xml',
        'views/res_config.xml'
    ],
    'demo': [],
    'images': ['static/description/thumbnails.png'],
    'qweb': ['static/src/xml/widget_places.xml'],
    'installable': True,
    'uninstall_hook': 'uninstall_hook',
}
