odoo.define('website_support.new_help_page', function (require) {
'use strict';

    var core = require('web.core');
    var base = require('web_editor.base');
    var WebsiteNewMenu = require("website.newMenu");
    var wUtils = require('website.utils');
    var rpc = require('web.rpc');
    var weContext = require('web_editor.context');

    var _t = core._t;

    WebsiteNewMenu.include({
        actions: _.extend({}, WebsiteNewMenu.prototype.actions || {}, {
            new_help_page: 'new_help_page',
        }),

        new_help_page: function() {

             rpc.query({
			    model: 'website.support.help.groups',
				method: 'name_search',
				args: [],
				context: weContext.get()
		     }).then(function(action_ids){
                 wUtils.prompt({
                     id: "editor_new_help_page",
                     window_title: _t("New Help Page"),
                     select: "Select Help Group",
                     init: function (field) {
                         return action_ids;
                     },
                 }).then(function (cat_id) {
                     document.location = '/helppage/new?group_id=' + cat_id;
                 });
            });
        },
    });
});


odoo.define('website_support.new_help_group', function (require) {
'use strict';

    var core = require('web.core');
    var base = require('web_editor.base');
    var WebsiteNewMenu = require("website.newMenu");
    var wUtils = require('website.utils');

    var _t = core._t;

    WebsiteNewMenu.include({
        actions: _.extend({}, WebsiteNewMenu.prototype.actions || {}, {
            new_help_group: 'new_help_group',
        }),

        new_help_group: function() {
            wUtils.prompt({
                id: "editor_new_help_group",
                window_title: _t("New Help Group"),
                input: _t("Help Group"),
                init: function () {

                }
            }).then(function (val, field, $dialog) {
                if (val) {
                    var url = '/helpgroup/new/' + encodeURIComponent(val);
                    document.location = url;
                }
            });
        },

    });
});