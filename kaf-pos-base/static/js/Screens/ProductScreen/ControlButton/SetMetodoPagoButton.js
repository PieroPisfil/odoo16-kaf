odoo.define('kaf-pos-base.SetMetodoPagoButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class SetMetodoPagoButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        
        get currentOrder() {
            return this.env.pos.get_order();
        }
        get currentMetodoPagoName() {
            return this.currentOrder.forma_de_pago_pe ? this.currentOrder.forma_de_pago_pe.name
                : this.env._t('Método de Pago');
        }
        async onClick() {
            const currentMetodoPago = this.currentOrder.forma_de_pago_pe;
            const metodopagoPosList = [];
            for (let element of this.env.pos.db.forma_de_pago_pe_alt){
                metodopagoPosList.push({
                    id: element.id,
                    label: element.name,
                    isSelected: currentMetodoPago 
                        ? element.id === currentMetodoPago.id
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

                /////Se pone los precios a cero o a precio de POS segun sea la forma de pago
                if(this.currentOrder.forma_de_pago_pe.code === 'garantia'){
                    for (let line of this.currentOrder.orderlines) {
                        line.set_unit_price(0);
                    }
                }
                else{
                    for (let line of this.currentOrder.orderlines) {
                        line.set_unit_price(line.product.get_price(this.currentOrder.pricelist, line.get_quantity(), line.get_price_extra()));
                    }
                }
                //Removemos las líneas de pago seleccionadas antes de cambiar el método de pago
                if(selectedMetodoPago != selectedMetodoPagoAnterior){
                    var lines = this.currentOrder.paymentlines;
                    var empty = [];
                    for ( var i = 0; i < lines.length; i++) {
                        empty.push(lines[i]);
                    }
                    for (var i = 0; i < empty.length; i++){
                        this.currentOrder.remove_paymentline(empty[i]);
                    }
                }
                //this.currentOrder.trigger('change');
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
