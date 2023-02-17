odoo.define('kaf-whatsapp-pos.ReceiptScreen', function (require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    const { onMounted, useRef, status } = owl;
    const { Printer } = require('point_of_sale.Printer');
    /* 
    const { is_email } = require('web.utils');
    const { useErrorHandlers, onChangeOrder } = require('point_of_sale.custom_hooks');
    const AbstractReceiptScreen = require('point_of_sale.AbstractReceiptScreen'); */

    const ReceiptScreenKaf = ReceiptScreen => 
        class extends ReceiptScreen  {
            setup() {
                super.setup();
                const order = this.currentOrder;
                const partner = order.get_partner();
                this.orderUiState = order.uiState.ReceiptScreen;
                this.orderUiState['inputWhatsapp'] = this.orderUiState.inputWhatsapp || (partner && partner.phone) || '';
                this.orderReceipt = useRef('order-receipt');
            }
            
            async onSendWhatsapp(){
                if(!this.orderUiState.inputWhatsapp){return;}
                let number_phone = this.orderUiState.inputWhatsapp
                let resultado
                number_phone = number_phone.split(" ").join("").replace('+','');
                const regex = /^[0-9]*$/;
                if(!regex.test(number_phone)){
                    this.orderUiState['whatsappSuccessful'] = false;
                    this.orderUiState['whatsappNotice'] = this.env._t('Error al enviar, teléfono mal escrito.');
                    return
                }
                //console.log(number_phone)
                try {
                    this.orderUiState['whatsappNotice'] = this.env._t('Enviando...');
                    resultado = await this._sendReceiptToCustomerWhatsapp(number_phone)
                    if(!resultado['error']){
                        this.orderUiState['whatsappSuccessful'] = true;
                        this.orderUiState['whatsappNotice'] = this.env._t('Verificar Envío ✅');
                    }
                    else{
                        this.orderUiState['whatsappSuccessful'] = false;
                        this.orderUiState['whatsappNotice'] = this.env._t(resultado['message']);
                    }
                } catch (error) {
                    this.orderUiState['whatsappSuccessful'] = false;
                    this.orderUiState['whatsappNotice'] = this.env._t('Error al enviar, por favor intente de nuevo o verificar configuracion de api.');
                }
            }
            async _sendReceiptToCustomerWhatsapp(number_phone) {
                let response
                const printer = new Printer(null, this.env.pos);
                const receiptString = this.orderReceipt.el.innerHTML;
                const ticketImage = await printer.htmlToImg(receiptString);
                const order = this.currentOrder;
                const partner = order.get_partner();
                const orderName = order.get_name();
                const orderPartner = { email: this.orderUiState.inputEmail, name: partner ? partner.name : this.orderUiState.inputEmail };
                const order_server_id = this.env.pos.validated_orders_name_server_id_map[orderName];
                response = await this.rpc({
                    model: 'pos.order',
                    method: 'send_ticket_whatsapp',
                    args: [[order_server_id], number_phone, orderName, orderPartner, ticketImage],
                });
                return response
            }  
        }

    Registries.Component.extend(ReceiptScreen, ReceiptScreenKaf);

    return ReceiptScreen;
});
