/** @odoo-module **/
/*
    Copyright 2025 Bernat Obrador APSL-Nagarro (bobrador@apsl.net).
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import * as Chrome from "@point_of_sale/../tests/tours/helpers/ChromeTourMethods";
import * as PaymentScreen from "@point_of_sale/../tests/tours/helpers/PaymentScreenTourMethods";
import * as PosOrderToSaleOrderScreen from "./helpers/SaleStockFromFsmPosMethods.esm";
import * as ProductScreenPos from "@point_of_sale/../tests/tours/helpers/ProductScreenTourMethods";
import * as ProductScreenSale from "@pos_sale/../tests/helpers/ProductScreenTourMethods";
import * as ReceiptScreen from "@point_of_sale/../tests/tours/helpers/ReceiptScreenTourMethods";
import * as TicketScreen from "@point_of_sale/../tests/tours/helpers/TicketScreenTourMethods";

import {registry} from "@web/core/registry";

const ProductScreen = {...ProductScreenPos, ...ProductScreenSale};

export function saleStockDraftFromPosFsmSteps() {
    return [
        ProductScreen.confirmOpeningPopup(),
        ProductScreen.clickHomeCategory(),
        ProductScreen.addOrderline("Whiteboard Pen", "1"),
        ProductScreen.addOrderline("Wall Shelf Unit", "1"),
        ProductScreen.clickPartnerButton(),
        ProductScreen.clickCustomer("Addison Olson"),
        PosOrderToSaleOrderScreen.clickCreateOrderButton(),
        PosOrderToSaleOrderScreen.clickCreateDraftOrderButton(),
        ProductScreen.clickQuotationButton(),
        ProductScreen.selectFirstOrder(),
        ProductScreen.clickPayButton(),
        PaymentScreen.clickPaymentMethod("Cash"),
        PaymentScreen.clickValidate(),
        Chrome.endTour(),
    ].flat();
}

registry.category("web_tour.tours").add("SaleStockDraftFromPosFsmTour", {
    test: true,
    url: "/pos/ui",
    steps: () => saleStockDraftFromPosFsmSteps(),
});

registry.category("web_tour.tours").add("SaleStockPartialRefundFromPosFsmTour", {
    test: true,
    url: "/pos/ui",
    steps: () =>
        [
            ...saleStockDraftFromPosFsmSteps(),
            ReceiptScreen.isShown(),
            ReceiptScreen.clickNextOrder(),
            ProductScreen.clickHomeCategory(),
            ProductScreen.clickRefund(),
            TicketScreen.filterIs("Paid"),
            TicketScreen.selectOrder("-"),
            TicketScreen.partnerIs("Addison Olson"),
            ProductScreen.pressNumpad("1"),
            TicketScreen.confirmRefund(),
            ProductScreen.clickPayButton(),
            PaymentScreen.clickPaymentMethod("Cash"),
            PaymentScreen.clickValidate(),
            Chrome.endTour(),
        ].flat(),
});

registry.category("web_tour.tours").add("SaleStockFullRefundFromPosFsmTour", {
    test: true,
    url: "/pos/ui",
    steps: () =>
        [
            ProductScreen.confirmOpeningPopup(),
            ProductScreen.clickHomeCategory(),
            ProductScreen.addOrderline("Whiteboard Pen", "1"),
            ProductScreen.clickPartnerButton(),
            ProductScreen.clickCustomer("Addison Olson"),
            PosOrderToSaleOrderScreen.clickCreateOrderButton(),
            PosOrderToSaleOrderScreen.clickCreateDraftOrderButton(),
            ProductScreen.clickQuotationButton(),
            ProductScreen.selectFirstOrder(),
            ProductScreen.clickPayButton(),
            PaymentScreen.clickPaymentMethod("Cash"),
            PaymentScreen.clickValidate(),
            ReceiptScreen.isShown(),
            ReceiptScreen.clickNextOrder(),
            ProductScreen.clickHomeCategory(),
            ProductScreen.clickRefund(),
            TicketScreen.filterIs("Paid"),
            TicketScreen.selectOrder("-"),
            TicketScreen.partnerIs("Addison Olson"),
            ProductScreen.pressNumpad("1"),
            TicketScreen.confirmRefund(),
            ProductScreen.clickPayButton(),
            PaymentScreen.clickPaymentMethod("Cash"),
            PaymentScreen.clickValidate(),
            Chrome.endTour(),
        ].flat(),
});
