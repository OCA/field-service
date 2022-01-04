odoo.define("fieldservice_timeline.CustomFilterItem", function (require) {
    "use strict";

    const {DatePicker, DateTimePicker} = require("web.DatePickerOwl");
    const Domain = require("web.Domain");
    const DropdownMenuItem = require("web.DropdownMenuItem");
    const {FIELD_OPERATORS, FIELD_TYPES} = require("web.searchUtils");
    const field_utils = require("web.field_utils");
    const patchMixin = require("web.patchMixin");
    const {useModel} = require("web/static/src/js/model.js");
    const {hooks} = owl; // eslint-disable-line
    const {useSubEnv} = hooks;

    class TimelineviewCustomfillter extends DropdownMenuItem {
        constructor() {
            super(...arguments);
            useSubEnv({
                searchModel: this.props.searchModel,
            });
            this.model = useModel("searchModel");

            this.canBeOpened = true;
            this.state.conditions = [];
            this.fields = Object.values(this.props.fields)
                .filter((field) => this._validateField(field))
                .concat({string: "ID", type: "id", name: "id"})
                .sort(({string: a}, {string: b}) => (a > b ? 1 : a < b ? -1 : 0));
            this.DECIMAL_POINT = this.env._t.database.parameters.decimal_point;
            this.OPERATORS = FIELD_OPERATORS;
            this.FIELD_TYPES = FIELD_TYPES;

            // Add default empty condition
            this._addDefaultCondition();
        }
        _validateField(field) {
            return (
                !field.deprecated &&
                field.searchable &&
                FIELD_TYPES[field.type] &&
                field.relation !== "mail.message" &&
                field.name !== "message_ids" &&
                field.name !== "id"
            );
        }
        _addDefaultCondition() {
            const condition = {
                field: 0,
                operator: 0,
            };
            this._setDefaultValue(condition);
            this.state.conditions.push(condition);
        }
        _setDefaultValue(condition) {
            const fieldType = this.fields[condition.field].type;
            const genericType = FIELD_TYPES[fieldType];
            const operator = FIELD_OPERATORS[genericType][condition.operator];
            // Logical value
            switch (genericType) {
                case "id":
                case "number":
                    condition.value = 0;
                    break;
                case "date":
                    condition.value = [moment()];
                    if (operator.symbol === "between") {
                        condition.value.push(moment());
                    }
                    break;
                case "datetime":
                    condition.value = [moment("00:00:00", "hh:mm:ss")];
                    if (operator.symbol === "between") {
                        condition.value.push(moment("23:59:59", "hh:mm:ss"));
                    }
                    break;
                case "selection":
                    const [firstValue] = this.fields[condition.field].selection[0];
                    condition.value = firstValue;
                    break;
                default:
                    condition.value = "";
            }
            if (["float", "monetary"].includes(fieldType)) {
                condition.displayedValue = `0${this.DECIMAL_POINT}0`;
            } else {
                condition.displayedValue = String(condition.value);
            }
        }
        _onDateChanged(condition, valueIndex, ev) {
            condition.value[valueIndex] = ev.detail.date;
        }

        _onFieldSelect(condition, ev) {
            Object.assign(condition, {
                field: ev.target.selectedIndex,
                operator: 0,
            });
            this._setDefaultValue(condition);
        }

        _onOperatorSelect(condition, ev) {
            condition.operator = ev.target.selectedIndex;
            this._setDefaultValue(condition);
        }
        _onValueInput(condition, ev) {
            if (!ev.target.value) {
                return this._setDefaultValue(condition);
            }
            let {type} = this.fields[condition.field];
            if (type === "id") {
                type = "integer";
            }
            if (FIELD_TYPES[type] === "number") {
                try {
                    condition.value = field_utils.parse[type](ev.target.value);
                    condition.displayedValue = ev.target.value;
                } catch (err) {
                    ev.target.value = condition.displayedValue;
                }
            } else {
                condition.value = condition.displayedValue = ev.target.value;
            }
        }
        _onApply() {
            const preFilters = this.state.conditions.map((condition) => {
                const field = this.fields[condition.field];
                const type = this.FIELD_TYPES[field.type];
                const operator = this.OPERATORS[type][condition.operator];
                const descriptionArray = [field.string, operator.description];
                const domainArray = [];
                let domainValue = [];
                if ("value" in operator) {
                    domainValue = [operator.value];
                } else if (["date", "datetime"].includes(type)) {
                    domainValue = condition.value.map((val) =>
                        field_utils.parse[type](val, {type}, {timezone: true})
                    );
                    const dateValue = condition.value.map((val) =>
                        field_utils.format[type](val, {type}, {timezone: false})
                    );
                    descriptionArray.push(
                        `"${dateValue.join(" " + this.env._t("and") + " ")}"`
                    );
                } else {
                    domainValue = [condition.value];
                    descriptionArray.push(`"${condition.value}"`);
                }
                if (operator.symbol === "between") {
                    domainArray.push(
                        [field.name, ">=", domainValue[0]],
                        [field.name, "<=", domainValue[1]]
                    );
                } else {
                    domainArray.push([field.name, operator.symbol, domainValue[0]]);
                }
                const preFilter = {
                    description: descriptionArray.join(" "),
                    domain: Domain.prototype.arrayToString(domainArray),
                    type: "filter",
                };
                return preFilter;
            });
            this.model.dispatch("createNewFilters", preFilters);
            this.state.open = false;
            this.state.conditions = [];
            this._addDefaultCondition();
        }
        _onRemoveCondition(conditionIndex) {
            this.state.conditions.splice(conditionIndex, 1);
        }
    }
    TimelineviewCustomfillter.components = {DatePicker, DateTimePicker};
    TimelineviewCustomfillter.props = {
        fields: Object,
        action: Object,
        breadcrumbs: false,
        searchMenuTypes: Object,
        view: false,
        views: Object,
        searchModel: false,
    };
    TimelineviewCustomfillter.template = "fieldservice_timeline.CustomFilterItem";

    return patchMixin(TimelineviewCustomfillter);
});
