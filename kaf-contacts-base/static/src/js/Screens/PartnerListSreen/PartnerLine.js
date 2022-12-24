odoo.define('kaf-contacts-base.ClientLine', function(require) {
    'use strict';

    const ClientLine = require('point_of_sale.ClientLine');
    const Registries = require('point_of_sale.Registries');

    const ClientLineKaf = ClientLine => 
        class extends ClientLine {
            _clickEditPersonalizado() {
                $('#edit-client-button').click()
                setTimeout(() => {
                    $('#boton-guardar-reemplazo').attr('hidden', true)
                    $('#boton-guardar-original').attr('hidden', false)
                    $('.client-name').attr('readonly', true)
                    $('#vat').attr('readonly', true)
                    $("select[name='l10n_latam_identification_type_id']").attr('disabled', true) 
                    $("select[name='country_id']").attr('disabled', true)
                    $("select[name='l10n_pe_district']").attr('disabled', true)
                    $("select[name='city_id']").attr('disabled', true) 
                    $("input[name='city']").attr('readonly', true)
                    $("select[name='state_id']").attr('disabled', true)
                },100)
            }
        }

    Registries.Component.extend(ClientLine,ClientLineKaf);

    return ClientLine;
});
