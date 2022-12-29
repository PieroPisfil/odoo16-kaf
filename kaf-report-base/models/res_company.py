# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).#

from odoo import api, fields, models, tools
import logging
_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
	_inherit = 'res.company'
	
	proforma_config = fields.Many2one('report.settings', string="Configuración de Proforma")

	image_header_proforma = fields.Binary(string="Imagen de cabecera para la proforma", related="proforma_config.image_header_proforma", readonly=False)
	image_footer_proforma = fields.Binary(string="Imagen de pie de página para la proforma", related="proforma_config.image_footer_proforma", readonly=False)
