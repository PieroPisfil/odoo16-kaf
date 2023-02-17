# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    whatsapp_api_url = fields.Char(string='URL de app', default='http://api:3333')
    whatsapp_instancia = fields.Many2one('whatsapp.instancia','Instancia de Whatsapp',domain="[('state','=','activa'),('company_id', '=', id)]")
    whatsapp_key = fields.Integer(string='Key de app', related='whatsapp_instancia.name', copy=False, readonly=True, store=True)
    whatsapp_token = fields.Char(string='Token de app', copy=False)
