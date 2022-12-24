odoo.define('kaf-contacts-base.models', function(require) {
    "use strict";
  
var models = require('point_of_sale.models');
var OrderSuper = models.Order;
var _posModelSuper = models.PosModel.prototype;

models.load_fields("res.company", ["street_name"]);
models.load_fields("res.partner", ["l10n_latam_identification_type_id","city_id","l10n_pe_district","state_sunat","condition_sunat","company_type"]);
models.load_fields("res.currency", ["currency_unit_label"]);

models.Order = models.Order.extend({
    // initialize: function (attributes, options) {
    //     var res = OrderSuper.prototype.initialize.apply(this, arguments);
    //     return res;
    // },
    export_for_printing: function(){
        var res = OrderSuper.prototype.export_for_printing.apply(this, arguments); 
        var company = this.pos.company;      
        res['company']['street_name'] = company.street_name;
        return res;
    },
});

models.load_models([{
    model: 'l10n_latam.identification.type',
    fields: ["name"],
    //domain: function(self){return [['country_id.code', '=', 'PE']]},
    loaded: function(self, doc_types){
/*         self.docu_by_id = {}
        _.each(doc_types, function(doc) {
        self.docu_by_id[doc.id] = doc.id
        }); */
        self.doc_types = doc_types;
    },
}]);

models.load_models([{
    model: 'res.city',
    fields: ["name","state_id"],
    loaded: function(self, cities_id){
        self.cities_id = cities_id;
    },
}]);

models.load_models([{
    model: 'l10n_pe.res.city.district',
    fields: ["name","city_id"],
    loaded: function(self, districts){
        self.districts = districts;
    },
}]);

models.PosModel = models.PosModel.extend({
    initialize: function (session, attributes) {
        var contact_model = _.find(this.models,function(model){
            return model.model === 'res.partner';
        });
        contact_model.fields.push('l10n_latam_identification_type_id');
        contact_model.fields.push('city_id');
        contact_model.fields.push('l10n_pe_district');
        return _posModelSuper.initialize.call(this,session,attributes);
    }
});

})
