/* Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).*/

odoo.define("fieldservice_website_sale.payment_form", (require) => {
    "use strict";

    const checkoutForm = require("payment.checkout_form");
    const manageForm = require("payment.manage_form");

    const salePaymentMixin = {
        // --------------------------------------------------------------------------
        // Private
        // --------------------------------------------------------------------------

        /**
         * Add the delivery date and time range to the transaction route params.
         *
         * @override method from payment.payment_form_mixin
         * @private
         * @param {String} provider - The provider of the selected payment option's acquirer
         * @param {Number} paymentOptionId - The id of the selected payment option
         * @param {String} flow - The online payment flow of the selected payment option
         * @returns {Object} The extended transaction route params
         */
        _prepareTransactionRouteParams: function () {
            const transactionRouteParams = this._super(...arguments);

            return {
                ...transactionRouteParams,
                selected_date: this.txContext.selectedDate || null,
                selected_time_range: this.txContext.selectedTimeRange || null,
            };
        },

        /**
         * Handle the Pay button click event.
         *
         * Ensures that the delivery date and time range are passed in the transaction context.
         *
         * @private
         * @param {Event} ev
         * @returns {undefined}
         */
        _onClickPay: async function (ev) {
            ev.stopPropagation();
            ev.preventDefault();

            const selectedDate = $('form[name="o_payment_checkout"]').data(
                "selected_date"
            );
            const selectedTimeRange = $('form[name="o_payment_checkout"]').data(
                "selected_time_range"
            );

            this.txContext.selectedDate = selectedDate;
            this.txContext.selectedTimeRange = selectedTimeRange;
            this._super(...arguments);
        },
    };

    checkoutForm.include(salePaymentMixin);
    manageForm.include(salePaymentMixin);
});
