odoo.define('kaf-pos-base.PaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const PaymentScreenVat = PaymentScreen =>
        class extends PaymentScreen {
            setup() {
                super.setup();
				//this.orderReceiptdd = useRef('order-receipt');
	        }
            async _finalizeValidation() {
                await super._finalizeValidation(...arguments);
                setTimeout(() => {
                    $('#button-refresh-ticket').click()
                },300)
            }
            toggleIsToInvoiceFactura() {
                // click_invoice
                this.currentOrder.set_to_invoice_factura(!this.currentOrder.is_to_invoice_factura());
                this.render(true);
            }
            toggleIsToInvoiceBoleta() {
                // click_invoice
                this.currentOrder.set_to_invoice_boleta(!this.currentOrder.is_to_invoice_boleta());
                this.render(true);
            }
            toggleIsToInvoiceRecibo() {
                // click_invoice
                this.currentOrder.set_to_invoice_recibo(!this.currentOrder.is_to_invoice_recibo());
                this.render(true);
            }
        }
        

    Registries.Component.extend(PaymentScreen, PaymentScreenVat);

    return PaymentScreen;
})
