# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PosSession(models.Model):
    _inherit = 'pos.session'

######## Cargar campos y modelos nuevos #####################################################

    @api.model
    def _pos_ui_models_to_load(self):
        models_to_load = super(PosSession, self)._pos_ui_models_to_load()
        new_models = [
            #"l10n_latam.identification.type",
            "res.city",
            #"l10n_pe.res.city.district",
            ]
        for new_model in new_models:
            models_to_load.append(new_model)
        return models_to_load
    
    def _loader_params_res_city(self):
        return {'search_params': {'domain': [], 'fields': ["name","state_id"]}}

######## Cargar campos de modelos ya subidos en el codigo original de Odoo###################

    def _loader_params_res_company(self):
        res = super(PosSession, self)._loader_params_res_company()
        res['search_params']['fields'].append("street")
        return res
    
    def _loader_params_res_partner(self):
        res = super(PosSession, self)._loader_params_res_partner()
        new_fields = ["l10n_latam_identification_type_id","city_id","l10n_pe_district","state_sunat","condition_sunat","company_type"]
        for new_field in new_fields:
            res['search_params']['fields'].append(new_field)
        return res
    
    def _loader_params_res_currency(self):
        res = super(PosSession, self)._loader_params_res_currency()
        res['search_params']['fields'].append("currency_unit_label")
        return res

    def _loader_params_res_currency(self):
        res = super(PosSession, self)._loader_params_res_currency()
        res['search_params']['fields'].append("currency_unit_label")
        return res