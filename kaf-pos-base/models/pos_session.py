# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PosSession(models.Model):
    _inherit = 'pos.session'

    ######## Cargar campos y modelos nuevos #####################################################

    @api.model
    def _pos_ui_models_to_load(self):
        models_to_load = super(PosSession, self)._pos_ui_models_to_load()
        new_models = [
            "account.journal",
            ]
        for new_model in new_models:
            models_to_load.append(new_model)
        return models_to_load
    
    def _loader_params_account_journal(self):
        return {'search_params': {'domain': [('type', '=', ['sale'])], 'fields': ["id","name","tipo_comprobante_nombre",]}}
    def _get_pos_ui_account_journal(self, params):
        return self.env['account.journal'].search_read(**params['search_params'])

######## Cargar campos de modelos ya subidos en el codigo original de Odoo ###################

    # def _loader_params_pos_config(self):
    #     res = super(PosSession, self)._loader_params_pos_config()
    #     new_fields = ["invoice_journal_factura_id","invoice_journal_boleta_id","invoice_journal_recibo_venta_id","envio_automatico_cpe"]
    #     for new_field in new_fields:
    #         res['search_params']['fields'].append(new_field)
    #     return res