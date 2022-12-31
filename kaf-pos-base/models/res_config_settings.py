# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_invoice_journal_factura_id = fields.Many2one(related='pos_config_id.invoice_journal_factura_id', readonly=False)
    pos_invoice_journal_boleta_id = fields.Many2one(related='pos_config_id.invoice_journal_boleta_id', readonly=False)
    pos_invoice_journal_recibo_venta_id = fields.Many2one(related='pos_config_id.invoice_journal_recibo_venta_id', readonly=False)
    pos_envio_automatico_cpe = fields.Boolean(related='pos_config_id.envio_automatico_cpe', string="Envío Automático CPE")
    # invoice_journal_ticket_intercambio_id = fields.Many2one("account.journal", string="Diario de Tickets", domain=lambda self: "[('type', 'in', ['sale']), ('tipo_comprobante','=',%s), ('pe_invoice_code','=','')]" % self.env.ref('kaf-account-base.recibo_caja_1').id)