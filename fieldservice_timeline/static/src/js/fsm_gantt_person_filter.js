odoo.define('fsm_gantt.person_filter', function (require) {
    'use strict';

    var TimelineRenderer = require('web_timeline.TimelineRenderer');
    var session = require('web.session');
    var search_filters = require('web.search_filters');
    var core = require('web.core');
    var _t = core._t;

    TimelineRenderer.include({

        /**
         * Init
         */
        init : function () {
            this._super.apply(this, arguments);

            // Initilaize propositions
            this.propositions = [];
        },

        /**
         * Do Search
         * Parameters:
         * @param {Array} domains
         * @param {Array} contexts
         * @param {Array} group_bys
         * @returns Array
         */
        do_search : function (domains, contexts, group_bys) {
            var self = this;
            self.last_domains = domains;
            self.last_contexts = contexts;

            // Select the group by
            var n_group_bys = [];
            if (this.arch.attrs.default_group_by) {
                n_group_bys = this.arch.attrs.default_group_by.split(',');
            }
            if (group_bys.length) {
                n_group_bys = group_bys;
            }
            self.last_group_bys = n_group_bys;

            /* Gather the fields to get
             */
            var fields = _.compact(_.map(['date_start',
                'date_delay', 'date_stop', 'progress'], function (key) {
                return self.arch.attrs[key] || '';
            }));
            fields = _.uniq(fields.concat(
                _.pluck(this.colors, 'field').concat(n_group_bys)));
            return this._rpc({
                model: this.modelName,
                method: 'search_read',
                fields: fields,
                args: [domains],
                kwargs: {context: contexts},
            }).then(function (r) {
                return self.on_data_loaded(r, n_group_bys, true);
            });
        },

        /**
         * Search data related to user filter
         * Parameters:
         * @param {Array} domains
         * @param {Array} contexts
         * @param {Array} group_bys
         * @param {Array} user_ids
         * @returns Array
         */
        do_search_related_user_filter : function (domains,
            contexts, group_bys, user_ids) {
            var self = this;

            /* Select the group by
             */
            var n_group_bys = [];
            if (this.arch.attrs.default_group_by) {
                n_group_bys = this.arch.attrs.default_group_by.split(',');
            }
            if (group_bys.length) {
                n_group_bys = group_bys;
            }

            /* Gather the fields to get
             */
            var fields = _.compact(_.map(['date_start',
                'date_delay', 'date_stop', 'progress'], function (key) {
                return self.arch.attrs[key] || '';
            }));
            fields = _.uniq(fields.concat(
                _.pluck(this.colors, 'field').concat(n_group_bys)));
            return this._rpc({
                model: this.modelName,
                method: 'search_read',
                fields: fields,
                args: [domains],
                kwargs: {context: contexts},
            }).then(function (r) {
                return self.on_user_data_loaded(r, n_group_bys, true, user_ids);
            });
        },

        /**
         * On user data loaded
         * Parameters:
         * @param {Array} events
         * @param {Array} group_bys
         * @param {Object} adjust_window
         * @param {Array} user_ids
         * @returns Object
         */
        on_user_data_loaded : function (events,
            group_bys, adjust_window, user_ids) {
            var self = this;
            var ids = _.pluck(events, 'id');
            return this._rpc({
                model: this.modelName,
                method: 'name_get',
                args: [
                    ids,
                ],
                context: this.getSession().user_context,
            }).then(function (names) {
                var nevents = _.map(events, function (event) {
                    return _.extend({
                        __name: _.detect(names, function (name) {
                            return name[0] === event.id;
                        })[1],
                    }, event);
                });
                return self.on_user_data_loaded_2(nevents,
                    group_bys, adjust_window, user_ids);
            });
        },

        /**
         * On user data loaded 2
         * Parameters:
         * @param {Array} events
         * @param {Array} group_bys
         * @param {Object} adjust_window
         * @param {Array} user_ids
         */
        on_user_data_loaded_2 : function (events,
            group_bys, adjust_window, user_ids) {
            var self = this;
            var data = [];
            var groups = [];
            this.grouped_by = group_bys;
            _.each(events, function (event) {
                if (event[self.date_start]) {
                    data.push(self.event_data_transform(event));
                }
            });

            /**
             * Get the groups
             * Parameters:
             * @param {Array} events
             * @param {Array} group_bys
             * @returns events
             */
            var split_groups = function (events, group_bys) {
                if (group_bys.length === 0) {
                    return events;
                }
                groups = [];
                groups.push({id:-1, content: _t('-')});
                _.each(events, function (event) {
                    var group_name = event[_.first(group_bys)];
                    if (group_name) {
                        var group = _.find(groups, function (group) {
                            return _.isEqual(group.id, group_name[0]);
                        });
                        if (group === undefined) {
                            group = {id: group_name[0], content: group_name[1]};
                            groups.push(group);
                        }
                    }
                });
                return groups;
            };
            groups = split_groups(events, group_bys);
            _.each(user_ids, function (user) {
                var group = _.find(groups, function (group) {
                    return _.isEqual(group.id, user.id);
                });
                if (group === undefined) {
                    group = {id: user.id,
                        content: user.name};
                    groups.push(group);
                }
            });

            this.timeline.setGroups(groups);
            this.timeline.setItems(data);
            var mode = !this.mode || this.mode === 'fit';
            var adjust = _.isUndefined(adjust_window) || adjust_window;
            if (mode && adjust) {
                this.timeline.fit();
            }
        },

        /**
         * Apply/clear User Filter
         * @param {Object} clear
         */
        apply_clear_user_filter : function (clear) {
            var self = this;
            if (clear) {
                self.user_domains = false;
                self.$el.find(
                    '#user_filer .o_searchview_extended_prop_field').val('');
                self.$el.find(
                    '#user_filer .o_searchview_extended_prop_field').change();
                self.$el.find(
                    '#user_filer .o_searchview_extended_prop_field').val(
                    'category_id');
                self.$el.find(
                    '#user_filer .o_searchview_extended_prop_field').change();
                self.do_search(
                    self.last_domains, self.last_contexts, self.last_group_bys);
            } else {
                var filters = _.invoke(this.propositions, 'get_filter');
                var domain = filters[0] && filters[0].attrs &&
                    filters[0].attrs.domain ? filters[0].attrs.domain : false;

                /* New method call improved by Sandip on 2018-09-21 */
                if (domain) {
                    this._rpc({
                        model: 'fsm.person',
                        method: 'search',
                        args: [domain],
                        kwargs: {context: session.user_context},
                    }).then(function (user_ids) {
                        var list_user_ids = [];
                        $.each(user_ids, function (index, value) {
                            var id = value;
                            var name = '';
                            for (var i in self.res_users[0]) {
                                if (self.res_users[0][i].id === id) {
                                    name = self.res_users[0][i].name;
                                }
                            }
                            list_user_ids.push({'id':id, 'name':name});
                        });
                        var ids = user_ids;
                        ids.push(false);
                        self.user_domains = ['person_id', 'in', ids];
                        var temp_domain = [];
                        if (self.last_domains) {
                            temp_domain = _.clone(self.last_domains);
                        }
                        temp_domain.push(self.user_domains);
                        self.do_search_related_user_filter(temp_domain,
                            self.last_contexts,
                            self.last_group_bys,
                            list_user_ids);
                    });
                }
            }
        },

        /**
         * On start
         * @returns this._super()
         */
        start : function () {
            var self = this;

            /* Bind User Filter Apply/Clear Click Event */
            this.$el.find('.oe_timeline_button_apply').click(
                $.proxy(this.on_apply_clicked, this));
            this.$el.find('.oe_timeline_button_clear').click(
                $.proxy(this.on_clear_clicked, this));

            /* Fetch User Fields And Append To Timeline View. */
            self._rpc({
                model: 'fsm.person',
                method: 'fields_get',
            }).then(function (fields) {
                self.user_filter = true;
                var prop =
                    new search_filters.ExtendedSearchProposition(self, fields);
                self.propositions.push(prop);
                prop.appendTo(self.$el.find('#user_filer'));
                self.$el.find(
                    '#user_filer .o_searchview_extended_delete_prop').hide();
                self.$el.find('#user_filer .o_or_filter').hide();
            });
            return this._super();
        },

        /**
         * Call apply User Filter
         */
        on_apply_clicked : function () {
            this.apply_clear_user_filter(false);
        },

        /**
         * Call Clear User Filter
         */
        on_clear_clicked : function () {
            this.apply_clear_user_filter(true);
        },
    });
});
