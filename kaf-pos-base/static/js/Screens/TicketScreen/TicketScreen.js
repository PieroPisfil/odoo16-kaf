odoo.define('kaf-pos-base.TicketScreen', function (require) {
    'use strict';
    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');

    const TicketScreenKaf = TicketScreen => 
        class extends TicketScreen  {
            getDocRelacionado(order) {
                let res = order.get_invoice_number()
                return res ? res : "";
            }
            getDateInvoice(order){
                let res = order.get_date_invoice()
                return res ? res : "";
            }
        }
    Registries.Component.extend(TicketScreen, TicketScreenKaf);

    return TicketScreen;
});
        