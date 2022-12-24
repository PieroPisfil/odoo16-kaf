# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    busqueda_ruc = fields.Selection([
        ('sinapi', 'Sin API de busqueda'),
        ('apisperu', 'APISPERU'),
        ('apiperu', 'APIPERU')], default="apisperu", string='API de búsqueda', required=True)
    token_apisperu = fields.Char(string='Token APIsPERU', default='')
    token_apiperu = fields.Char(string='Token APIPERU', default='')
