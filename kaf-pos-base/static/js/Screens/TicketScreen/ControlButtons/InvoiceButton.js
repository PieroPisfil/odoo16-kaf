odoo.define('kaf-pos-base.InvoiceButton', function (require) {
    'use strict';

    const { useListener } = require("@web/core/utils/hooks");
    const { isConnectionError } = require('point_of_sale.utils');
    const InvoiceButton = require('point_of_sale.InvoiceButton');
    const Registries = require('point_of_sale.Registries');

    const InvoiceButtonKaf = InvoiceButton => 
        class extends InvoiceButton  {
            async _invoiceOrder() {
                const order = this.props.order;
                if (!order) return;

                const orderId = order.backendId;

                // Part 0. If already invoiced, print the invoice.
                if (this.isAlreadyInvoiced) {
                    await this._downloadInvoice(orderId);
                    return;
                }

                // Part 1: Handle missing partner.
                // Write to pos.order the selected partner.
                if (!order.get_partner()) {
                    const { confirmed: confirmedPopup } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Need customer to invoice'),
                        body: this.env._t('Do you want to open the customer list to select customer?'),
                    });
                    if (!confirmedPopup) return;

                    const { confirmed: confirmedTempScreen, payload: newPartner } = await this.showTempScreen(
                        'PartnerListScreen'
                    );
                    if (!confirmedTempScreen) return;

                    await this.rpc({
                        model: 'pos.order',
                        method: 'write',
                        args: [[orderId], { partner_id: newPartner.id }],
                        kwargs: { context: this.env.session.user_context },
                    });
                }
                
                // Part 2: Invoice the order.
                const diariosList = [];
                if (this.env.pos.config.invoice_journal_factura_id){
                    diariosList.push({
                        id: 1,
                        label: "FacturaCPE",
                        item: this.env.pos.config.invoice_journal_factura_id,
                    });
                }
                if (this.env.pos.config.invoice_journal_boleta_id){
                    diariosList.push({
                        id: 2,
                        label: "BoletaCPE",
                        item: this.env.pos.config.invoice_journal_boleta_id,
                    });
                }
                if (this.env.pos.config.invoice_journal_recibo_venta_id){
                    diariosList.push({
                        id: 3,
                        label: "Recibo de Caja",
                        item: this.env.pos.config.invoice_journal_recibo_venta_id,
                    });
                }
                const { confirmed: confirmed2, payload: selectedJournalInvoice } = await this.showPopup(
                    'ConfirmSelectPopup',{
                        confirmText: this.env._t('Select'),
                        cancelText: this.env._t('Exit'),
                        title: this.env._t('Diario de facturación?'),
                        body: this.env._t('Seleccionar el diario de facturación'),
                        list: diariosList,
                    })
                if (!confirmed2) return;
                
                await this.rpc(
                    {
                        model: 'pos.order',
                        method: 'action_pos_order_invoice',
                        args: [orderId],
                        kwargs: { context: this.env.session.user_context },
                    },
                    {
                        timeout: 30000,
                        shadow: true,
                    }
                );
                // Part 3: Download invoice.
                await this._downloadInvoice(orderId);
                this.trigger('order-invoiced', orderId);
            }
        }

    Registries.Component.extend(InvoiceButton, InvoiceButtonKaf);

    return InvoiceButton;
});
