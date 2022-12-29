odoo.define('kaf-pos-base.SetMetodoPagoButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class SetMetodoPagoButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        mounted() {
            this.env.pos.get('orders').on('add remove change', () => this.render(), this);
            this.env.pos.on('change:selectedOrder', () => this.render(), this);
        }
        willUnmount() {
            this.env.pos.get('orders').off('add remove change', null, this);
            this.env.pos.off('change:selectedOrder', null, this);
        }
        get currentOrder() {
            return this.env.pos.get_order();
        }
        get currentMetodoPagoName() {
            return this.currentOrder.forma_de_pago_pe ? this.currentOrder.forma_de_pago_pe.name
                : this.env._t('Método de Pago');
        }
        async onClick() {
            var self = this;
            const currentMetodoPago = this.currentOrder.forma_de_pago_pe;
            const metodopagoPosList = [];
            for (let element of this.env.pos.db.forma_de_pago_pe_alt){
                metodopagoPosList.push({
                    id: element.id,
                    label: element.name,
                    isSelected: currentMetodoPago ? element.id === currentMetodoPago.id
                    : false,
                    item: element,
                })
            }
            const { confirmed, payload: selectedMetodoPago } = await this.showPopup(
                'SelectionPopup',
                {
                    title: this.env._t('Seleccionar Método de pago'),
                    list: metodopagoPosList,
                }
            );
            if (confirmed) {
                let selectedMetodoPagoAnterior = this.currentOrder.forma_de_pago_pe
                this.currentOrder.forma_de_pago_pe = selectedMetodoPago;

                if(this.currentOrder.forma_de_pago_pe.code === 'garantia'){
                    for (let line of this.currentOrder.orderlines.models) {
                        line.set_unit_price(0);
                    }
                }
                else{
                    for (let line of this.currentOrder.orderlines.models) {
                        line.set_unit_price(line.product.get_price(this.currentOrder.pricelist, line.get_quantity(), line.get_price_extra()));
                    }
                    //this.currentOrder.set_pricelist(this.currentOrder.pricelist;
                }
                //Removemos las líneas de pago seleccionadas antes de cambiar el método de pago
                if(selectedMetodoPago != selectedMetodoPagoAnterior){
                    //console.log(this.currentOrder.paymentlines)
                    var lines = this.currentOrder.paymentlines.models;
                    var empty = [];
                    for ( var i = 0; i < lines.length; i++) {
                        empty.push(lines[i]);
                    }
                    for (var i = 0; i < empty.length; i++){
                        this.currentOrder.remove_paymentline(empty[i]);
                        //this.currentOrder.paymentlines.remove(this.currentOrder.paymentlines.models[i])
                    }
                }

                this.currentOrder.trigger('change');
            }
        }
    }
    SetMetodoPagoButton.template = 'SetMetodoPagoButton';

    ProductScreen.addControlButton({
        component: SetMetodoPagoButton,
        condition: function() {
            return true;
        },
        position: ['before', 'SetPricelistButton'],
    });

    Registries.Component.add(SetMetodoPagoButton);

    return SetMetodoPagoButton;
});
