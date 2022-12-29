odoo.define('kaf-pos-base.models', function(require) {
    "use strict";
  
    var models = require('point_of_sale.models');
    var OrderSuper = models.Order;
    var OrderlineSuper = models.Orderline;
    var PosModelSuper = models.PosModel;
    var PosDB = require('point_of_sale.DB');
    var PosDBSuper = PosDB;
    const rpc = require('web.rpc');

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
    models.load_models(
        [   
            {
                model: 'account.journal',
                fields: ["id","name","tipo_comprobante_nombre"],
                //domain: function(self){return [['type', '=', ['sale']],]; },
                ids: function(self){ return [self.config.invoice_journal_factura_id[0], self.config.invoice_journal_boleta_id[0], self.config.invoice_journal_recibo_venta_id[0]]; },
                loaded: function(self, journals){    
                    self.journal_ids = journals;
                    self.db.add_journals(journals);
                },
            }
        ]   
    );

    models.load_fields('pos.config', ['invoice_journal_factura_id', 'invoice_journal_boleta_id', 'invoice_journal_recibo_venta_id','envio_automatico_cpe']);
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var res = PosModelSuper.prototype.initialize.apply(this, arguments);
            this.db = new PosDB();
            return res;
        }
    });

    models.Orderline = models.Orderline.extend({
        initialize: function (attributes, options) {
            var res = OrderlineSuper.prototype.initialize.apply(this, arguments);
            return res;
        },
        export_for_printing: function(){
            var res = OrderlineSuper.prototype.export_for_printing.apply(this, arguments);
            res['product_default_code'] = this.get_product().default_code || '-';
            return res
        },

    })

    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            this.pos = options.pos;
            this.forma_de_pago_pe = this.pos.db.forma_de_pago_pe_alt[0];
            this.to_invoice_factura    = false;
            this.to_invoice_boleta     = false;
            this.to_invoice_recibo     = false;
            this.invoice_journal = false;
            this.numero_doc_relacionado = false;
            this.amount_text = false;
            this.sunat_qr_code_char = false;
            var res = OrderSuper.prototype.initialize.apply(this, arguments);
            return res;
        },

        /**
        * @param {object} json JSON representing one PoS order.
        */
       //funcion que se llama cuando se va a reimprimir y otras cosas pos-emisión
        init_from_JSON: function(json) {
            OrderSuper.prototype.init_from_JSON.apply(this, arguments);
            this.invoice_journal_name = json.invoice_journal_name ? json.invoice_journal_name : false;
            this.numero_doc_relacionado = json.numero_doc_relacionado ? json.numero_doc_relacionado : false;
            this.forma_de_pago_pe = this.get_forma_de_pago_pe(json.forma_de_pago_pe) ? this.get_forma_de_pago_pe(json.forma_de_pago_pe) : false;
            this.amount_text = json.amount_text || false
            this.sunat_qr_code_char = json.sunat_qr_code_char || false
        },

        set_to_invoice_factura: function(to_invoice) {
            this.assert_editable();
            this.to_invoice_boleta     = false;
            this.to_invoice_recibo     = false;
            this.to_invoice_factura = to_invoice;
            this.invoice_journal = to_invoice ? this.pos.config.invoice_journal_factura_id  : false; 
            this.to_invoice = to_invoice;
        },
        is_to_invoice_factura: function(){
            return this.to_invoice_factura;
        },
        set_to_invoice_boleta: function(to_invoice) {
            this.assert_editable();
            this.to_invoice_factura    = false;
            this.to_invoice_recibo     = false;
            this.to_invoice_boleta = to_invoice;
            this.invoice_journal = to_invoice ? this.pos.config.invoice_journal_boleta_id : false; 
            this.to_invoice = to_invoice;
        },
        is_to_invoice_boleta: function(){
            return this.to_invoice_boleta;
        },
        set_to_invoice_recibo: function(to_invoice) {
            this.assert_editable();
            this.to_invoice_factura    = false;
            this.to_invoice_boleta     = false;
            this.to_invoice_recibo = to_invoice;
            this.invoice_journal = to_invoice ? this.pos.config.invoice_journal_recibo_venta_id : false; 
            this.to_invoice = to_invoice;
        },
        is_to_invoice_recibo: function(){
            return this.to_invoice_recibo;
        },
        
        //Esta funcion tmbn sirve para guaradar en la base de datos en el modelo pos.order
        //esto sirve para guardar datos en el modelo pos.order//////////////////
        export_as_JSON: function () {
            var json = OrderSuper.prototype.export_as_JSON.apply(this, arguments);
            json['invoice_journal'] = this.invoice_journal[0];
            json['forma_de_pago_pe'] = this.forma_de_pago_pe.code;
            json['date_invoice'] = moment(new Date().getTime()).format('YYYY/MM/DD');
            return json;
        },

        //esto sirve para que se imprima por primera vez o después la orden(solo poner campos para la generacion de la orden, no obtencion de campos de factura)///////////////
        export_for_printing: function(){
            var res = OrderSuper.prototype.export_for_printing.apply(this, arguments);
            res['invoice'] = {
                invoice_journal_name: this.get_journal_name(this.invoice_journal[0]) || 'Ticket POS',
            }
            res['forma_de_pago_pe'] = this.forma_de_pago_pe;
            return res
        },

        get_journal_name: function(journal_id){
            if (this.invoice_journal_name) {
                return this.invoice_journal_name
            }
            if (!journal_id){
                return false;
            }
            return this.pos.db.get_journal_nombre(journal_id);
        },

        get_invoice_number: function () {
            if (this.numero_doc_relacionado) {
                return this.numero_doc_relacionado
            }
            return false
        },
        get_forma_de_pago_pe: function (forma_de_pago_pe_code) {
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
        },

        get_amount_text: function () {
            if (this.amount_text) {
                return this.amount_text
            }
            return false
        },

        get_qr_code: function () {
            var qr_string = this.sunat_qr_code_char;
            var qrcodesingle = new QRCode(false, {width : 80, height : 80, correctLevel : QRCode.CorrectLevel.Q});
            qrcodesingle.makeCode(qr_string);
            let qrdibujo = qrcodesingle.getDrawing();
            return qrdibujo._canvas_base64;
        }
    });

})
