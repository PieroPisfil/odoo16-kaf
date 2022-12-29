# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PosConfigImage(models.Model):
    _inherit = 'pos.config'

    image = fields.Binary(string='Image')


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    #invoice_journal_ids = fields.Many2many(comodel_name='account.journal', string='Diarios de venta', domain="[('type', 'in', ['sale'])]")
    invoice_journal_factura_id = fields.Many2one(string='Diario de factura Perú', comodel_name='account.journal', domain=lambda self: "[('type', 'in', ['sale']), ('tipo_comprobante','=',%s), ('pe_invoice_code','=','01')]" % self.env.ref('kaf-account-base.factura_1').id)
    invoice_journal_boleta_id = fields.Many2one("account.journal", string="Diario de boleta Perú", domain=lambda self: "[('type', 'in', ['sale']), ('tipo_comprobante','=',%s), ('pe_invoice_code','=','03')]" % self.env.ref('kaf-account-base.boleta_1').id)
    invoice_journal_recibo_venta_id = fields.Many2one("account.journal", string="Diario de Recibos", domain=lambda self: "[('type', 'in', ['sale']), ('tipo_comprobante','=',%s)]" % self.env.ref('kaf-account-base.recibo_caja_1').id)
    envio_automatico_cpe = fields.Boolean(default=True, string="Envío Automático CPE")
    # invoice_journal_ticket_intercambio_id = fields.Many2one("account.journal", string="Diario de Tickets", domain=lambda self: "[('type', 'in', ['sale']), ('tipo_comprobante','=',%s), ('pe_invoice_code','=','')]" % self.env.ref('kaf-account-base.recibo_caja_1').id)