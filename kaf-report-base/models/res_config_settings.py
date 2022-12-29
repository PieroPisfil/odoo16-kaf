# -*- coding: utf-8 -*-
# License MIT #

from odoo import api, fields, models, tools

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	proforma_config = fields.Many2one(comodel_name='report.settings', related="company_id.proforma_config" , readonly=False)


