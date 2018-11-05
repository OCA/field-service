odoo.define('web_google_maps.FieldsRegistry', function(require) {
    'use strict';

    var registry = require('web.field_registry');
    var GplacesAutocomplete = require('web_google_maps.GplaceAutocompleteFields');

    registry.add('gplaces_address_autocomplete', GplacesAutocomplete.GplacesAddressAutocompleteField);
    registry.add('gplaces_autocomplete', GplacesAutocomplete.GplacesAutocompleteField);

});