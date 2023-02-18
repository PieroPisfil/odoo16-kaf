# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tipo_producto_kaf = fields.Selection([
        ('fotocopiadora', 'Es Fotocopiadora'),
        ('toner', 'Es Toner'),
        ('repuesto', 'Es Repuesto'),
        ('none', 'Ninguno')], string="Tipo Producto", help="Ayuda a saber qué tipo de producto es", default='none', required=True)
    modelo_fotocopiadora_id=fields.Many2one('datasheet',"Fotocopiadora relacionada")
    # fotocopiadoras_ids_toner=fields.Many2many('datasheet','fotocopiers_ids_toner')