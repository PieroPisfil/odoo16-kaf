odoo.define('kaf-contacts-base.models', function(require) {
    "use strict";
  
var { PosGlobalState } = require('point_of_sale.models');
var { Order } = require('point_of_sale.models');
var Registries = require('point_of_sale.Registries');

    const PosGlobalStateKaf = (PosGlobalState) => class PosGlobalStateKaf extends PosGlobalState {
        async _processData(loadedData) {
            this.doc_types = loadedData['l10n_latam.identification.type'];
            super._processData(...arguments);
        }
    }
    Registries.Model.extend(PosGlobalState, PosGlobalStateKaf);

    // const CustomOrder = (Order) => class CustomOrder extends Order {
    //     export_for_printing() {
    //         var result = super.export_for_printing(...arguments);
    //         result.client = this.get_partner();
    //         return result;
    //     }
    // }
    // Registries.Model.extend(Order, CustomOrder); 

    
});
