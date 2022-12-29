# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models, _, api
# librería para mensajes
from odoo.exceptions import UserError, ValidationError

logger = logging.getLogger(__name__)

class AccountJournal(models.Model):
   
  _inherit = "account.journal"

  is_cpe = fields.Boolean('Habilitado para envío:',help="Está habilitado para envío electrónico?")
  is_synchronous = fields.Boolean("Es síncrono")
  is_synchronous_anull = fields.Boolean("Anulación síncrona", default=True)
  credit_note_id = fields.Many2one(comodel_name="account.journal", string="Nota de credito", 
    domain="[('type','in', ['sale', 'purchase']), ('pe_invoice_code', '=', '07')]")
  dedit_note_id = fields.Many2one(comodel_name="account.journal", string="Nota de debito", 
    domain="[('type','in', ['sale', 'purchase']), ('pe_invoice_code', '=', '08')]")
  pe_invoice_code = fields.Selection(selection="_get_pe_invoice_code", string="Tipo de data")
  tipo_comprobante = fields.Many2one(comodel_name="tipo.comprobante", string="Tipo de comprobante")
  tipo_comprobante_nombre = fields.Char(related="tipo_comprobante.titulo_en_documento",store=True, readonly=False)
  #pe_payment_method = fields.Selection(selection="_get_pe_payment_method", string="Metodo de pago")

  usar_secuencia_propia = fields.Boolean('Secuencia personalizada', help="Usar una secuencia propia como se hacia en otras versiones, al marcar esta opción y emitir un comprobante con este diario ya no se podrá usar el correlativo por defecto de odoo14 para este diario")
  sequence_id = fields.Many2one('ir.sequence', string='Secuencia de diario',
    help="Este campo contiene la información relacionada con la numeración de los asientos de este diario.", copy=False)
  sequence_number_next = fields.Integer(string='Siguiente numero', help='El siguiente número de secuencia se utilizará para la próxima factura.',
    compute='_compute_seq_number_next',inverse='_inverse_seq_number_next')
  # Usado para los diarios tipo banco cuyo numero de cuenta se desea mostrar en las cotizaciones y/o facturas
  mostrar_en_venta = fields.Boolean('Mostrar en venta')

  @api.model
  def _get_pe_invoice_code(self):
    return self.env['pe.datas'].get_selection("PE.TABLA10")

  @api.depends('sequence_id.use_date_range', 'sequence_id.number_next_actual')
  def _compute_seq_number_next(self):
    # Calcule 'sequence_number_next' según la secuencia actual en uso, una ir.sequence o una ir.sequence.date_range.      
    for journal in self:
      if journal.sequence_id:
        sequence = journal.sequence_id._get_current_sequence()
        journal.sequence_number_next = sequence.number_next_actual
      else:
        journal.sequence_number_next = 1

  def _inverse_seq_number_next(self):
  # Inverse 'sequence_number_next' to edit the current sequence next number.
    for journal in self:
      if journal.sequence_id and journal.sequence_number_next:
        sequence = journal.sequence_id._get_current_sequence()
        sequence.sudo().number_next = journal.sequence_number_next


  @api.model
  def _get_sequence_prefix(self, code):
    prefix = code.upper()
    return prefix + '-'
  
  @api.model
  def _create_sequence(self, vals):
		# Create new no_gap entry sequence for every new Journal
    code = vals['code'] if 'code' in vals else self.code
    prefix = self._get_sequence_prefix(code)
    seq_name = code
    seq = {
			'name': _('%s Sequence') % seq_name,
			'implementation': 'no_gap',
			'prefix': prefix,
			'padding': 8,
			'number_increment': 1,
			'use_date_range': True,
		}
    if 'company_id' in vals:
      seq['company_id'] = vals['company_id']
    seq = self.env['ir.sequence'].create(seq)
    seq_date_range = seq._get_current_sequence()
    seq_date_range.number_next = vals.get('sequence_number_next', 1)
    return seq


  def write(self, vals):
    for journal in self:
      if ('code' in vals and journal.code != vals['code']):
        if self.env['account.move'].search([('journal_id', '=', self.id)], limit=1):
          raise UserError('Este diario ya contiene elementos, por lo que no puede modificar su nombre corto.')
        new_prefix = self._get_sequence_prefix(vals['code'])
        journal.sequence_id.write({'prefix': new_prefix})
      if ('usar_secuencia_propia' in vals and not journal.sequence_id and vals['usar_secuencia_propia']):
        vals.update({'sequence_id': self.sudo()._create_sequence(vals).id})
			# """if ('usar_secuencia_propia' in vals and vals['usar_secuencia_propia'] == False and journal.usar_secuencia_propia == True):
			# 	if self.env['account.move'].search([('journal_id', '=', self.id)], limit=1):
			# 		raise UserError('Este diario ya contiene elementos, por lo que no puede volver a utilizar el correlativo propio de odoo.')"""
    result = super(AccountJournal, self).write(vals)
    return result


  @api.model
  def create(self, vals):
    if not vals.get('sequence_id') and 'usar_secuencia_propia' in vals and vals['usar_secuencia_propia']:
      vals.update({'sequence_id': self.sudo()._create_sequence(vals).id})
    result = super(AccountJournal, self).create(vals)
    return result