odoo.define("kaf-pos-base.pos_image_field", function (require) {
    "use strict";
    const Registries = require('point_of_sale.Registries');
    const Chrome = require('point_of_sale.Chrome');
    const PosLogoChrome = (Chrome) =>
        class extends Chrome {
            get imageUrl() {
                if (this.env.pos){
                    if (this.env.pos.config){
                        if (this.env.pos.config.image != false){
                            return true;
                        }else{
                            return false
                        }
                    }
                }
            }
        };
    Registries.Component.extend(Chrome, PosLogoChrome);
    return Chrome;
});