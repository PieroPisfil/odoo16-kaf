# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ReportSettings(models.Model):
    _name = 'report.settings'
    _description = 'Configuración de Reportes'

    name = fields.Char(string="Nombre de plantilla")
    image_header_proforma = fields.Binary(string="Imagen de cabecera para la proforma", readonly=False)
    image_footer_proforma = fields.Binary(string="Imagen de pie de página para la proforma", readonly=False)