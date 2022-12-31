odoo.define('kaf-pos-base.OrderReceipt', function(require) {
    'use strict';

    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const Registries = require('point_of_sale.Registries');

    const OrderReceiptCPE = OrderReceipt =>
        class extends OrderReceipt {
	        get order() {
	            return this.receiptEnv.order;
	        }
        };

    Registries.Component.extend(OrderReceipt, OrderReceiptCPE);

    return OrderReceipt;
});
