odoo.define('kaf-pos-base.models', function(require) {
    "use strict";
    
    var PosDB = require('point_of_sale.DB');
    var PosDBSuper = PosDB;
    var { PosGlobalState } = require('point_of_sale.models');
    var { Order } = require('point_of_sale.models');
    var { Orderline } = require('point_of_sale.models');
    var Registries = require('point_of_sale.Registries');

    PosDB = PosDB.extend({
        init: function (options) {
            this.journal_by_id = {};
            this.journal_by_nombre = {};
            this.sequence_by_id = {};
            this.journal_sequence_by_id = {};
            this.forma_de_pago_pe_alt = [
                {'id':0,'code': 'contado', 'name':'CONTADO'},
                {'id':1,'code': 'credito', 'name':'CRÉDITO'},
                {'id':2,'code': 'garantia', 'name':'POR GARANTÍA'},]
            //this.invoice_numbers=[];
            return PosDBSuper.prototype.init.apply(this, arguments);
        },

        add_journals: function (journals) {
            if (!journals instanceof Array) {
                journals = [journals];
            }
            for (var i = 0, len = journals.length; i < len; i++) {
                this.journal_by_id[journals[i].id] = journals[i];
                this.journal_by_nombre[journals[i].id] = journals[i].tipo_comprobante_nombre;
                //this.journal_sequence_by_id[journals[i].id] = journals[i].sequence_id[0];
            }
        },
        get_journal_id: function (journal_id) {
            return this.journal_by_id[journal_id];
        },
        get_journal_nombre: function (journal_id) {
            return this.journal_by_nombre[journal_id];
        },

    });

    const PosGlobalStateKaf = (PosGlobalState) => class PosGlobalStateKaf extends PosGlobalState {
        constructor(obj) {
            super(obj);
            this.db = new PosDB();  
        }

        async _processData(loadedData) {
            this.journal_ids = loadedData['account.journal'];
            this.db.add_journals(this.journal_ids);
            super._processData(...arguments);
        }
    }
    Registries.Model.extend(PosGlobalState, PosGlobalStateKaf);

    const CustomOrderline = (Orderline) => class CustomOrderline extends Orderline {
        export_for_printing() {
            var result = super.export_for_printing(...arguments);
            result['product_default_code'] = this.get_product().default_code || '-';
            return result;
        }
    }
    Registries.Model.extend(Orderline, CustomOrderline); 

    const CustomOrder = (Order) => class CustomOrder extends Order {
        constructor(obj, options) {
            super(...arguments);
            options  = options || {};
            //this.pos = options.pos;
            this.forma_de_pago_pe = this.forma_de_pago_pe ? this.forma_de_pago_pe : this.pos.db.forma_de_pago_pe_alt[0];
            this.to_invoice_factura    = false;
            this.to_invoice_boleta     = false;
            this.to_invoice_recibo     = false;
            this.invoice_journal = this.invoice_journal ? this.invoice_journal : false;
        }
        /**
        * Initialize PoS order from a JSON string.
        *
        * If the order was created in another session, the sequence number should be changed so it doesn't conflict
        * with orders in the current session.
        * Else, the sequence number of the session should follow on the sequence number of the loaded order.
        *
        * @param {object} json JSON representing one PoS order.
        */
        
        init_from_JSON(json) {
            super.init_from_JSON(...arguments);
            this.invoice_journal_name = json.invoice_journal_name ? json.invoice_journal_name : false;
            this.numero_doc_relacionado = json.numero_doc_relacionado ? json.numero_doc_relacionado : false;
            this.see_taxes = json.see_taxes ? json.see_taxes : false;
            this.date_invoice = json.date_invoice ? json.date_invoice : false;
            this.forma_de_pago_pe = this.get_forma_de_pago_pe(json.forma_de_pago_pe) ? this.get_forma_de_pago_pe(json.forma_de_pago_pe) : false;
            this.amount_text = json.amount_text || false
            this.sunat_qr_code_char = json.sunat_qr_code_char || false
        }
        set_to_invoice_factura(to_invoice) {
            this.assert_editable();
            this.to_invoice_boleta     = false;
            this.to_invoice_recibo     = false;
            this.to_invoice_factura = to_invoice;
            this.invoice_journal = to_invoice ? this.pos.config.invoice_journal_factura_id  : false; 
            this.to_invoice = to_invoice;
        }
        is_to_invoice_factura(){
            return this.to_invoice_factura;
        }
        set_to_invoice_boleta(to_invoice) {
            this.assert_editable();
            this.to_invoice_factura    = false;
            this.to_invoice_recibo     = false;
            this.to_invoice_boleta = to_invoice;
            this.invoice_journal = to_invoice ? this.pos.config.invoice_journal_boleta_id : false; 
            this.to_invoice = to_invoice;
        }
        is_to_invoice_boleta(){
            return this.to_invoice_boleta;
        }
        set_to_invoice_recibo(to_invoice) {
            this.assert_editable();
            this.to_invoice_factura    = false;
            this.to_invoice_boleta     = false;
            this.to_invoice_recibo = to_invoice;
            this.invoice_journal = to_invoice ? this.pos.config.invoice_journal_recibo_venta_id : false; 
            this.to_invoice = to_invoice;
        }
        is_to_invoice_recibo(){
            return this.to_invoice_recibo;
        }
        //Esta funcion tmbn sirve para guaradar en la base de datos en el modelo pos.order
        //esto sirve para guardar datos en el modelo pos.order//////////////////
        // @override
        export_as_JSON() {
            var json = super.export_as_JSON(...arguments);
            json['invoice_journal'] = this.invoice_journal[0];
            json['forma_de_pago_pe'] = this.forma_de_pago_pe.code;
            //json['date_invoice'] = moment(new Date().getTime()).format('YYYY/MM/DD');
            return json;
        }

        //esto sirve para que se imprima por primera vez o después la orden(solo poner campos para la generacion de la orden, no obtencion de campos de factura)///////////////
        export_for_printing(){
            var res = super.export_for_printing(...arguments);
            res['invoice'] = {
                invoice_journal_name: this.get_journal_name(this.invoice_journal[0]) || 'Ticket POS',
                numero_doc_relacionado: this.numero_doc_relacionado || "********",
                see_taxes: this.get_see_taxes(this.numero_doc_relacionado) || false,
            }
            res['forma_de_pago_pe'] = this.forma_de_pago_pe;
            res['date_invoice'] = this.get_date_invoice();
            console.log(res)
            return res
        }
        get_date_invoice(){
            return this.date_invoice;
        }
        get_see_taxes(numero_doc_relacionado) {
            if(this.to_invoice_boleta || this.to_invoice_factura){
                return true
            }
            if(numero_doc_relacionado){            
                if(numero_doc_relacionado.includes('B',0) || numero_doc_relacionado.includes('F',0)){
                    return true
                }
            }
            return false
        }
        get_journal_name(journal_id){
            if (this.invoice_journal_name) {
                return this.invoice_journal_name
            }
            if (!journal_id){
                return false;
            }
            return this.pos.db.get_journal_nombre(journal_id);
        }
        get_invoice_number() {
            return this.numero_doc_relacionado
        }
        get_forma_de_pago_pe(forma_de_pago_pe_code) {
            var fpagos = this.pos.db.forma_de_pago_pe_alt;
            let ffpp = fpagos[0];
            if(forma_de_pago_pe_code){
                fpagos.forEach((fpago) => {
                    if(fpago.code === forma_de_pago_pe_code){
                        ffpp = fpago
                    }
                })
            }
            return ffpp
        }
        get_amount_text() {
            if (this.amount_text) {
                return this.amount_text
            }
            return false
        }
        get_qr_code() {
            var qr_string = this.sunat_qr_code_char ? this.sunat_qr_code_char : this.name;
            var qrcodesingle = new QRCode(false, {width : 80, height : 80, correctLevel : QRCode.CorrectLevel.Q});
            qrcodesingle.makeCode(qr_string);
            let qrdibujo = qrcodesingle.getDrawing();
            return qrdibujo._canvas_base64;
        }
    }
    Registries.Model.extend(Order, CustomOrder); 
})
