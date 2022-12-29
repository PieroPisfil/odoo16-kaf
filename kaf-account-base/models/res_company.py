# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    tipo_envio_sunat = fields.Selection([
        ('sinapi', 'Sin API de busqueda'),
        ('apipropio', 'API PROPIO'),
        ('nubefact', 'Nubefact (por implementar)')], default="apipropio", string='API de envío CPE', required=True)
    token_api_propio_sunat = fields.Char(string='Token API de envío CPE', default='')
    url_api_propio_sunat = fields.Char(string='URL de envío CPE', default='')
    modo_envio_cpe = fields.Selection([
        ('prueba','Prueba'),
        ('produccion','Producción')
    ], default="prueba", string="Modo de envío CPE")
    usuario_prueba_cpe = fields.Char(string="Usuario para Modo Prueba", default="MODDATOS")   
    password_prueba_cpe = fields.Char(string="Contraseña para Modo Prueba", default="moddatos")
    usuario_produccion_cpe = fields.Char(string="Usuario para Modo Produccion", default="MODDATOS")   
    password_produccion_cpe = fields.Char(string="Contraseña para Modo Produccion", default="moddatos")
