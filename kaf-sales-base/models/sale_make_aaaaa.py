# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class SaleAdvancePayment(models.TransientModel):
    #_name = "sale.advance.payment.inv.custom"
    _inherit = "sale.advance.payment.inv"

    tipo_comprobante_peru = fields.Selection([
        ('ticketintercambio', 'Ticket de Intercambio'),
        ('recibodecaja', 'Recibo de caja'),
        ('boleta', 'Boleta'),
        ('factura', 'Factura')
        ], string='Tipo de comprobante que desea', default='recibodecaja', required=True,
        help="Elija el comprobante que desea para poder hacer el comprobante")

    tipo_diario_peru = fields.Many2one('account.journal', domain = [('type', '=', 'sale')],
        string='Tipo de comprobante que desea', required=True, help="Elija el comprobante que desea para poder hacer el comprobante")