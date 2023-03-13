# -*- coding: utf-8 -*-

from odoo import fields, api, tools, models
from datetime import datetime
from odoo.exceptions import ValidationError
import pytz
import psycopg2
from odoo.tools import float_is_zero, float_round, float_repr, float_compare
import logging
from dateutil.parser import parse as parse_date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT

tz = pytz.timezone('America/Lima')

_logging = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _get_journal(self, id_journal):
        return self.env['account.journal'].search([
                ('id', '=', id_journal), 
                ('active', '=', True)
            ], limit=1).id

    #esto sirve para guardar al servidor en el modelo pos.order (independiente de generación de ticket)
    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['invoice_journal'] = ui_order.get('invoice_journal', False)
        f_pago = ui_order.get('forma_de_pago_pe', False)
        res['forma_de_pago_pe'] = f_pago
        return res

    #esto sirve para guardar al servidor la factura account.move
    def _prepare_invoice_vals(self):
        res = super(PosOrder, self)._prepare_invoice_vals()
        res['forma_de_pago_pe'] = self.forma_de_pago_pe or False
        res['journal_id'] = (self.invoice_journal.id or self.session_id.config_id.invoice_journal_id.id) 
        return res
    
    invoice_sequence_number = fields.Integer(string='Secuencia de números de factura', readonly=True, copy=False)
    invoice_journal = fields.Many2one('account.journal', string='Diario de facturas de ventas',   states={'draft': [('readonly', False)]}, readonly=True, domain="[('type', 'in', ['sale'])]", copy=False)
    invoice_journal_name = fields.Char(string='Nombre de diario', related='invoice_journal.tipo_comprobante.titulo_en_documento')
    numero_doc_relacionado = fields.Char(string='Doc. Relacionado', related='account_move.name', readonly=True, copy=False)
    forma_de_pago_pe = fields.Char(string="Forma de pago", readonly=True, default="contado", compute="_compute_forma_de_pago_pe")
    amount_text = fields.Char(related='account_move.amount_text', readonly=True, copy=False)
    sunat_qr_code_char = fields.Char(related="account_move.sunat_qr_code_char", readonly=True, copy=False)
    date_invoice = fields.Date("Fecha de factura", readonly=True, copy=False, related="account_move.invoice_date", store=True)

    #Funcion para poner en cache los campos de la orden despues de emitirla en la reimpresion
    def _export_for_ui(self, order):
        res = super(PosOrder, self)._export_for_ui(order)
        res['invoice_journal'] = order.invoice_journal.id
        res['invoice_journal_name'] = order.invoice_journal_name
        res['numero_doc_relacionado'] = order.numero_doc_relacionado
        res['forma_de_pago_pe'] = order.forma_de_pago_pe
        res['amount_text'] = order.amount_text
        res['date_invoice'] = order.date_invoice
        res['sunat_qr_code_char'] = order.sunat_qr_code_char
        return res
    
    #Esto no debería ir, solo para que complete la fomra de pago en contado y hacer pruebas, al terminar borrar el compute en el campo
    @api.depends("forma_de_pago_pe")
    def _compute_forma_de_pago_pe(self):
        for pos_order in self:
            if pos_order.account_move:
                pos_order.forma_de_pago_pe = pos_order.account_move.forma_de_pago_pe
            else:
                pos_order.forma_de_pago_pe = "contado"