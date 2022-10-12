odoo.define('fieldservice.fsm_gantt', function (require) {
    'use strict';

    var core = require('web.core');
    var time = require('web.time');
    var session = require('web.session');
    var TimelineRenderer = require('web_timeline.TimelineRenderer');
    var _t = core._t;

    TimelineRenderer.include({

        /**
         * Init Overrite
         * Parameters:
         * @param {Object} parent
         * @param {Object} state
         * @param {Array} params
         */
        init: function (parent, state, params) {
            var self = this;
            this._super.apply(this, arguments);
            this.modelName = params.model;
            this.mode = params.mode;
            this.options = params.options;
            this.permissions = params.permissions;
            this.timeline = params.timeline;
            this.date_start = params.date_start;
            this.date_stop = params.date_stop;
            this.date_delay = params.date_delay;
            this.colors = params.colors;
            this.fieldNames = params.fieldNames;
            this.dependency_arrow = params.dependency_arrow;
            this.view = params.view;
            this.modelClass = this.view.model;
            self.res_users = [];
            self.res_users_ids = [];

            // Find their matches
            if (this.modelClass.modelName == 'fsm.order'){
                this._rpc({
                    model: 'fsm.person',
                    method: 'get_person_information',
                    args: [
                        [session.uid], {}
                    ],
                }).then(function (result) {
                    self.res_users.push(result);
                    for (var r in result) {
                        self.res_users_ids.push(result[r].id);
                    }
                });
                // Find custom color if mentioned
                if (params.arch.attrs.custom_color === "true") {
                    this._rpc({
                        model: 'fsm.stage',
                        method: 'get_color_information',
                        args: [
                            [], {}
                        ],
                    }).then(function (result) {
                        self.colors = result;
                    });
                }
            }
        },

        /**
         * On data loaded 2
         * Parameters:
         * @param {Array} events
         * @param {Array} group_bys
         * @param {Object} adjust_window
         */
        on_data_loaded_2: function (events, group_bys, adjust_window) {
            var self = this;
            // Make the user filter clear
            if (this.modelClass.modelName == 'fsm.order'){
                self.$el.find(
                    '#user_filer .o_searchview_extended_prop_value input').val('');
                self.$el.find(
                    '#user_filer .o_searchview_extended_prop_field').val(
                    'category_id');
                self.$el.find(
                    '#user_filer .o_searchview_extended_prop_field').change();
                // Make the user filter clear
                var data = [];
                var groups = [];
                this.grouped_by = group_bys;
                _.each(events, function (event) {
                    if (event[self.date_start]) {
                        data.push(self.event_data_transform(event));
                    }
                });
                groups = self.split_groups(events, group_bys);
                if (group_bys[0] === 'person_id') {
                    var groups_user_ids = [];
                    for (var g in groups) {
                        groups_user_ids.push(groups[g].id);
                    }
                    // Find their matches
                    self._rpc({
                        model: 'fsm.person',
                        method: 'get_person_information',
                        args: [
                            [session.uid], {}
                        ],
                    }).then(function (result) {
                        self.res_users.push(result);
                        for (var r in result) {
                            self.res_users_ids.push(result[r].id);
                        }
                        for (var u in self.res_users_ids) {
                            if (!(self.res_users_ids[u] in groups_user_ids) ||
                                self.res_users_ids[u] !== -1) {

                                // Get User Name
                                var user_name = '-';
                                for (var n in self.res_users[0]) {
                                    if (self.res_users[0][n].id ===
                                        self.res_users_ids[u]) {
                                        user_name = self.res_users[0][n].name;
                                    }
                                }
                                var is_available = false;
                                for (var i in groups) {
                                    if (groups[i].id === self.res_users_ids[u]) {
                                        is_available = true;
                                    }
                                }
                                if (!is_available) {
                                    groups.push({
                                        id: self.res_users_ids[u],
                                        content: _t(user_name),
                                    });
                                }
                            }
                        }
                        self.timeline.setGroups(groups);
                        self.timeline.setItems(data);
                        var mode = !self.mode || self.mode === 'fit';
                        var adjust = _.isUndefined(adjust_window) || adjust_window;
                        self.timeline.setOptions({
                            orientation: 'top',
                        });
                        if (mode && adjust) {
                            self.timeline.fit();
                        }
                    });
                }
            }else{
                self.$el.find('#user_filer').addClass('o_hidden')
                self.$el.find('.oe_timeline_button_apply').addClass('o_hidden')
                self.$el.find('.oe_timeline_button_clear').addClass('o_hidden')
                self.$el.find('.oe_timeline_button_synch').addClass('o_hidden')
                self.$el.find('#person_filter').addClass('o_hidden')
                this._super.apply(this, arguments);
            }
        },

        /**
         * Transform Odoo event object to timeline event object
         * Parameters:
         * @param {Array} evt
         * @returns r
         */
        event_data_transform: function (evt) {
            var self = this;
            var date_start = new moment();
            var date_stop = null;
            var date_delay = evt[this.date_delay] || false,
                all_day = this.all_day ? evt[this.all_day] : false;

            if (all_day) {
                date_start = time.auto_str_to_date(
                    evt[this.date_start].split(' ')[0], 'start');
                if (this.no_period) {
                    date_stop = date_start;
                } else {
                    date_stop = this.date_stop ?
                        time.auto_str_to_date(
                            evt[this.date_stop].split(' ')[0], 'stop') : null;
                }
            } else {
                date_start = time.auto_str_to_date(evt[this.date_start]);
                date_stop = this.date_stop ?
                    time.auto_str_to_date(evt[this.date_stop]) : null;
            }

            if (!date_stop && date_delay) {
                date_stop =
                    moment(date_start).add(date_delay, 'hours').toDate();
            }

            var group = evt[self.last_group_bys[0]];
            if (group && group instanceof Array) {
                group = _.first(group);
            } else {
                group = -1;
            }
            _.each(self.colors, function (color) {
                if (eval('\'' + evt[color.field] +
                        '\' ' + color.opt + ' \'' + color.value + '\'')) {
                    self.color = color.color;
                } else if (eval('\'' + evt[color.field][1] +
                        '\' ' + color.opt + ' \'' + color.value + '\'')) {
                    self.color = color.color;
                }
            });

            var content = _.isUndefined(evt.__name) ?
                evt.display_name : evt.__name;
            if (this.arch.children.length) {
                content = this.render_timeline_item(evt);
            }

            var r = {
                'start': date_start,
                'content': content,
                'id': evt.id,
                'group': group,
                'evt': evt,
                'style': 'background-color: ' + self.color + ';',
            };

            /**
             * Check if the event is instantaneous,
             * if so, display it with a point on the timeline (no 'end')
             */
            if (date_stop && !moment(date_start).isSame(date_stop)) {
                r.end = date_stop;
            }
            self.color = null;
            return r;
        },
    });
});
