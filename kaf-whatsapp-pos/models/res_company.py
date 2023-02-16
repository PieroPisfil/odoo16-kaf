# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    whatsapp_api_url = fields.Char(string='URL de app', default='http://api:3333')
    whatsapp_key = fields.Char(string='Key de app', default='10')
    whatasapp_token = fields.Char(string='Token de app')
    whatsapp_qr = fields.Char(string='QR activa')
