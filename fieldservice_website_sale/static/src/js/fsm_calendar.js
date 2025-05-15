/* Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("fsm_website_sale_calendar", function (require) {
    "use strict";

    const animation = require("website.content.snippets.animation");
    const ajax = require("web.ajax");
    const time = require("web.time");

    const DATE_FORMAT = time.strftime_to_moment_format("%Y-%m-%d");

    var CalendarList = animation.Class.extend({
        selector: ".fsm_delivery_calendar",

        init: function () {
            this._fetch_calendar_config().then((configInfo) => {
                const number = Number(configInfo.max_date_number);
                const unit = configInfo.max_date_unit;

                this.datepicker_options = {
                    inline: true,
                    minDate: moment().add(1, "days"),
                    maxDate: moment().add(number, unit),
                    icons: {
                        previous: "fa fa-chevron-left",
                        next: "fa fa-chevron-right",
                    },
                    format: DATE_FORMAT,
                    useCurrent: false,
                    locale: moment.locale(),
                };
            });
            return this._super.apply(this, arguments);
        },

        start: function () {
            this._super.apply(this, arguments);

            this._fetch_route_info().then((routeInfo) => {
                if (routeInfo.route_assigned) {
                    this.$calendar = this.$target.find(".fsm_website_sale_calendar");
                    this.$timeRangeDropdown = this.$target.find("#time-range-dropdown");
                    this.$calendar.on(
                        "change.datetimepicker",
                        this.on_date_selected.bind(this)
                    );
                    this.$timeRangeDropdown.on(
                        "change",
                        this.on_time_range_selected.bind(this)
                    );

                    this.load_and_render_dates(moment());
                } else {
                    this._show_no_route_assigned_message();
                }
            });
        },

        _fetch_calendar_config: function () {
            return ajax.rpc("/fieldservice/get_calendar_config").then((data) => data);
        },

        _fetch_route_info: function () {
            return ajax.rpc("/fieldservice/get_route_info").then((data) => data);
        },

        _show_no_route_assigned_message: function () {
            const $noRouteMessage = this.$target.find(".no-enabled-dates-message");
            const $rowContainer = this.$target.find(".row");

            $noRouteMessage.removeClass("d-none");
            $rowContainer.addClass("d-none");
        },

        load_and_render_dates: function (when) {
            return this._fetch_enabled_and_blackout_days(when).then((data) => {
                this.render_calendar(data);
            });
        },

        _fetch_enabled_and_blackout_days: function (when) {
            return ajax
                .rpc("/fieldservice/get_enabled_days", {
                    start: when.format(DATE_FORMAT),
                    end: when.clone().add(4, "months").format(DATE_FORMAT),
                })
                .then((enabledData) => {
                    return ajax
                        .rpc("/fieldservice/get_blackout_days", {})
                        .then((blackoutData) => {
                            enabledData.blackout_days = blackoutData.disabled_dates;
                            return enabledData;
                        });
                });
        },

        render_calendar: function (data) {
            const enabledDays = data.enabled_days;
            const disabledDays = [0, 1, 2, 3, 4, 5, 6].filter(
                (day) => !enabledDays.includes(day)
            );

            const blackoutDates = data.blackout_days.map((date) =>
                moment(date, "YYYY-MM-DD")
            );
            const busyDates = data.busy_dates.map((date) => moment(date, "YYYY-MM-DD"));

            const disabledDates = [...blackoutDates, ...busyDates];

            this.$calendar.empty().datetimepicker({
                ...this.datepicker_options,
                daysOfWeekDisabled: disabledDays,
                disabledDates: disabledDates,
            });
        },

        on_date_selected: function (event) {
            const selectedDate = event.date;
            this._update_selected_date(selectedDate);
            this._fetch_time_ranges().then((timeRanges) => {
                this._populate_time_range_dropdown(timeRanges);
            });
        },

        on_time_range_selected: function (event) {
            const selectedTimeRange = event.target.value;
            this._update_selected_time_range(selectedTimeRange);
        },

        _fetch_time_ranges: function () {
            return ajax
                .rpc("/fieldservice/get_time_ranges")
                .then((response) => response.time_ranges);
        },

        _populate_time_range_dropdown: function (timeRanges) {
            const $dropdown = this.$timeRangeDropdown;

            $dropdown.empty();
            this._update_selected_time_range("");
            $dropdown.append(new Option(_("Select Time Range"), ""));

            timeRanges.forEach((timeRange) => {
                $dropdown.append(new Option(timeRange.name, timeRange.id));
            });
        },

        _update_selected_date: function (selectedDate) {
            const form = $('form[name="o_payment_checkout"]');
            form.data("selected_date", selectedDate.format("YYYY-MM-DD"));
        },

        _update_selected_time_range: function (selectedTimeRange) {
            const form = $('form[name="o_payment_checkout"]');
            form.data("selected_time_range", selectedTimeRange);
        },
    });

    animation.registry.fsm_website_sale_calendar = CalendarList;

    return {
        DATE_FORMAT: DATE_FORMAT,
    };
});
