# -*- coding: utf-8 -*-

from odoo import fields, models, api


class CopierBrand(models.Model):
    _name = "copier.brand"
    _inherit = ['image.mixin']

    name = fields.Char(string='Nombre de Marca')

    active = fields.Boolean(default=True)
