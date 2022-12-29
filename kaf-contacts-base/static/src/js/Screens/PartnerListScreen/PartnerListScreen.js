odoo.define('kaf-contacts-base.PartnerListScreen', function(require) {
    'use strict';

    const PartnerListScreen = require('point_of_sale.PartnerListScreen');
    const Registries = require('point_of_sale.Registries');
    const PartnerDetailsEdit = require('point_of_sale.PartnerDetailsEdit');

   const PartnerListScreenVat = PartnerListScreen => 
        class extends PartnerListScreen {
            _createPartnerEdit(){
                let valor_vat = $('input[id="buscar-input"]').val()
                let tipo_vat = 1;
                console.log(valor_vat)
                $('#button-new-partner-original').click();
                if (!valor_vat){
                    setTimeout(() => {
                        $('.l10n_latam_identification_type_id').click()
                        $(`.l10n_latam_identification_type_id option[value=""]`).attr('selected', 'selected')
                    },100)
                    console.log("entro a funcion no buscar")
                    return;
                }
                const regex = /^[0-9]*$/;
                if(valor_vat.length == 11 && regex.test(valor_vat) && (valor_vat.substr(0,2) == '20' || valor_vat.substr(0,2) == '10') ) {
                    tipo_vat = 4
                } else if(valor_vat.length == 8 && regex.test(valor_vat)){
                    tipo_vat = 5               
                } else if(valor_vat.length == 0){tipo_vat = 4}
                console.log(tipo_vat)
                setTimeout(() => {
                    $('#vat').val(`${valor_vat}`)
                    $(".l10n_latam_identification_type_id").val(`${tipo_vat}`)
                    $('#busqueda-datos').click()
                    $(`.l10n_latam_identification_type_id option[value=${tipo_vat}]`).attr('selected', 'selected')
                },100)
            }
            // _clickGuardar(){
            //     var self = this;
            //     let vat = $('#vat').val()
            //     let tipo_doc = $('.l10n_latam_identification_type_id').val()
            //     if(!vat){
            //         self.showPopup('ErrorTracebackPopup', {
            //             'title': 'Nro. de documento vacío',
            //             'body': 'Se necesita un Número de Documento, no debe estar vacío',
            //         });
            //         return;
            //     }
            //     if(!tipo_doc){
            //         self.showPopup('ErrorTracebackPopup', {
            //             'title': 'Tpo. de documento vacío',
            //             'body': 'Se necesita un Tipo de Documento, no debe estar vacío',
            //         });
            //         return;
            //     }
            //     rpc.query({
            //         model: 'res.partner',
            //         method: 'consulta_vat_existe',
            //         args: [vat],
            //     }).then(function(res) {
            //         console.log(res)
            //         if(res.error){
            //             self.showPopup('ErrorTracebackPopup', {
            //                 'title': 'No se podrá guardar contacto',
            //                 'body': `${res.message}`,
            //             });
            //             return;
            //         }
            //         $('#boton-guardar-original').click()
            //     })
            // }
    }

    Registries.Component.extend(PartnerListScreen,PartnerListScreenVat);

    return PartnerListScreen;
});
