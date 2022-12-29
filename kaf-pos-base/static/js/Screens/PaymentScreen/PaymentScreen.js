odoo.define('kaf-pos-base.PaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    // var ReceiptScreen = require('point_of_sale.ReceiptScreen');
    // var ReceiptScreenSuper = ReceiptScreen;
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session');
    const core = require('web.core');
    const _t = core._t;
    const QWeb = core.qweb;

    // ReceiptScreen = ReceiptScreen.extend({

    // })

    const PaymentScreenVat = PaymentScreen =>
        class extends PaymentScreen {
            constructor() {
	            super(...arguments);
				//this.orderReceiptdd = useRef('order-receipt');
	        }
            toggleIsToInvoiceFactura() {
                // click_invoice
                this.currentOrder.set_to_invoice_factura(!this.currentOrder.is_to_invoice_factura());
                this.render();
            }
            toggleIsToInvoiceBoleta() {
                // click_invoice
                this.currentOrder.set_to_invoice_boleta(!this.currentOrder.is_to_invoice_boleta());
                this.render();
            }
            toggleIsToInvoiceRecibo() {
                // click_invoice
                this.currentOrder.set_to_invoice_recibo(!this.currentOrder.is_to_invoice_recibo());
                this.render();
            }
            // async validateOrder(isForceValidate) {
            //     if(this.env.pos.config.cash_rounding) {
            //         if(!this.env.pos.get_order().check_paymentlines_rounding()) {
            //             this.showPopup('ErrorPopup', {
            //                 title: this.env._t('Rounding error in payment lines'),
            //                 body: this.env._t("The amount of your payment lines must be rounded to validate the transaction."),
            //             });
            //             return;
            //         }
            //     }
            //     if (await this._isOrderValid(isForceValidate)) {
            //         // remove pending payments before finalizing the validation
            //         for (let line of this.paymentLines) {
            //             if (!line.is_done()) this.currentOrder.remove_paymentline(line);
            //         }
            //     }
            // }

        }
        

    Registries.Component.extend(PaymentScreen, PaymentScreenVat);

    return PaymentScreen;
})
