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

    #esto sirve para guaradar al servidor en el modelo pos.order (independiente de generación de ticket)
    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['invoice_journal'] = ui_order.get('invoice_journal', False)
        reg_datetime = datetime.now(tz)
        fecha = reg_datetime.strftime("%Y-%m-%d")
        res['date_invoice'] = parse_date(ui_order.get('date_invoice', fecha)).strftime(DATE_FORMAT)
        f_pago = ui_order.get('forma_de_pago_pe', False)
        res['forma_de_pago_pe'] = f_pago
        return res

    #esto sirve para guardar al servidor la factura account.move
    def _prepare_invoice_vals(self):
        res = super(PosOrder, self)._prepare_invoice_vals()
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        res['invoice_date'] = self.date_invoice or self.date_order.astimezone(timezone).date()
        res['journal_id'] = (self.invoice_journal.id or self.session_id.config_id.invoice_journal_id.id) 
        res['forma_de_pago_pe'] = self.forma_de_pago_pe or False
        return res
    
    invoice_sequence_number = fields.Integer(string='Secuencia de números de factura', readonly=True, copy=False)
    invoice_journal = fields.Many2one('account.journal', string='Diario de facturas de ventas',   states={'draft': [('readonly', False)]}, readonly=True, domain="[('type', 'in', ['sale'])]", copy=False)
    invoice_journal_name = fields.Char(string='Nombre de diario', related='invoice_journal.tipo_comprobante.titulo_en_documento')
    numero_doc_relacionado = fields.Char(string='Doc. Relacionado', related='account_move.name', readonly=True, copy=False)
    date_invoice = fields.Date("Fecha de la factura")
    forma_de_pago_pe = fields.Char(string="Forma de pago", readonly=True)
    amount_text = fields.Char(related='account_move.amount_text', readonly=True, copy=False)
    sunat_qr_code_char = fields.Char(related="account_move.sunat_qr_code_char", readonly=True, copy=False)

    #Funcion para poner en cache los campos de la orden despues de emitirla en la reimpresion
    def _export_for_ui(self, order):
        res = super(PosOrder, self)._export_for_ui(order)
        res['invoice_journal'] = order.invoice_journal.id
        res['invoice_journal_name'] = order.invoice_journal_name
        res['numero_doc_relacionado'] = order.numero_doc_relacionado
        res['forma_de_pago_pe'] = order.forma_de_pago_pe
        res['amount_text'] = order.amount_text
        res['sunat_qr_code_char'] = order.sunat_qr_code_char
        return res
    