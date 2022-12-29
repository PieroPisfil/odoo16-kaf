# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _
from . import amount_to_text_es

class Currency(models.Model):
	_inherit = 'res.currency'
	
	# singular_name = fields.Char("Nombre singular")
	# plural_name = fields.Char("Nombre plural")
	# fraction_name = fields.Char("Nombre de la fracción")
	show_fraction = fields.Boolean("Mostrar fracción",default=True,copy=False)

	# pe_currency_code = fields.Selection('_get_pe_invoice_code', "Currrency Code")

	# @api.model
	# def _get_pe_invoice_code(self):
	# 	return self.env['pe.datas'].get_selection("PE.TABLA04")
	
	def amount_to_text(self, amount):
		self.ensure_one()
		currency = self.currency_unit_label or self.name or ""
		sufijo = self.currency_subunit_label or ""
		amount_text = amount_to_text_es.amount_to_text(amount, currency, sufijo, self.show_fraction) 
		return amount_text