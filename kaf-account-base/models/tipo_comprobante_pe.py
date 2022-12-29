# -*- coding: utf-8 -*-

from odoo import fields, models, api

class TipoComprobante(models.Model):
    _name = "tipo.comprobante"

    name = fields.Char(string="Nombre", required=True, copy=False)
    titulo_en_documento = fields.Char(string="Título en Documento", copy=False)
    code_api = fields.Char(string="Código", required=True, copy=False)
    es_cpe = fields.Boolean(string="Es CPE?",default=False)
    es_nota_credito_debito = fields.Boolean(string="Es nota de crédito o débito?",default=False)
    puede_tener_anticipo = fields.Boolean(string="Puede tener anticipo?",default=False)

    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if not vals.get('titulo_en_documento'):
            vals['titulo_en_documento'] = vals.get('name')
        result = super(TipoComprobante, self).create(vals)
        return result