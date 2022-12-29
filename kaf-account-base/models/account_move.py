from odoo import api, fields, models, _
# from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
# import odoo.addons.decimal_precision as dp
# from datetime import datetime
from collections import defaultdict
import json
from . import amount_to_text_es
from odoo.tools.misc import format_date
# import re
# from . import amount_to_text_es
from odoo.exceptions import UserError, ValidationError
# from odoo.tools.misc import format_date

try:
    import qrcode
    qr_mod = True
except:
    qr_mod = False
from base64 import encodebytes
from io import StringIO, BytesIO


import logging
_logging = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    forma_de_pago_pe = fields.Selection([
        ('contado','CONTADO'),
        ('credito','CRÉDITO'),
        ('garantia','POR GARANTÍA')
    ],string="Forma de Pago", default="contado", copy=False, required=True)

    stado_envio_sunat = fields.Boolean(string="Sunat aceptó el comprobante:", default=False, copy=False)
    json_api_envio = fields.Char(copy=False)
    json_api_rspt = fields.Char(copy=False)

    amount_text = fields.Char("Monto en letras", compute="_get_amount_text")

    sunat_qr_code_char = fields.Char('Char QR code',compute='_compute_qr_char')
    sunat_qr_code = fields.Binary('QR Code', compute='_compute_get_qr_code')
    sunat_hash = fields.Char('Hash de Sunat')

################################# CONVERTIR MONTO EN SU EQUIVALENTE EN LETRAS #####################################################
    @api.depends('amount_total')
    def _get_amount_text(self):
        for invoice in self:
            # fraction_name = invoice.currency_id.currency_subunit_label or ""
            amount_text = invoice.currency_id.amount_to_text(
                invoice.amount_total)
            invoice.amount_text = amount_text

######################## Para obtener el nombre del recibo, factura o boleta  #############################################
    def _compute_name(self):
        def journal_key(move):
            return (move.journal_id, move.journal_id.refund_sequence and move.move_type)

        def date_key(move):
            return (move.date.year, move.date.month)

        grouped = defaultdict(  # key: journal_id, move_type
            lambda: defaultdict(  # key: first adjacent (date.year, date.month)
                lambda: {
                    'records': self.env['account.move'],
                    'format': False,
                    'format_values': False,
                    'reset': False
                }
            )
        )
        self = self.sorted(lambda m: (m.date, m.ref or '', m.id))
        highest_name = self[0]._get_last_sequence(lock=False) if self else False

        # Group the moves by journal and month
        for move in self.filtered(lambda m: not m.journal_id.usar_secuencia_propia):
            if not highest_name and move == self[0] and not move.posted_before and move.date:
                # In the form view, we need to compute a default sequence so that the user can edit
                # it. We only check the first move as an approximation (enough for new in form view)
                pass
            elif (move.name and move.name != '/') or move.state != 'posted':
                try:
                    if not move.posted_before:
                        move._constrains_date_sequence()
                    # Has already a name or is not posted, we don't add to a batch
                    continue
                except ValidationError:
                    # Has never been posted and the name doesn't match the date: recompute it
                    pass
            group = grouped[journal_key(move)][date_key(move)]
            if not group['records']:
                # Compute all the values needed to sequence this whole group
                move._set_next_sequence()
                group['format'], group['format_values'] = move._get_sequence_format_param(move.name)
                group['reset'] = move._deduce_sequence_number_reset(move.name)
            group['records'] += move

        # Fusion the groups depending on the sequence reset and the format used because `seq` is
        # the same counter for multiple groups that might be spread in multiple months.
        final_batches = []
        for journal_group in grouped.values():
            journal_group_changed = True
            for date_group in journal_group.values():
                if (
                    journal_group_changed
                    or final_batches[-1]['format'] != date_group['format']
                    or dict(final_batches[-1]['format_values'], seq=0) != dict(date_group['format_values'], seq=0)
                ):
                    final_batches += [date_group]
                    journal_group_changed = False
                elif date_group['reset'] == 'never':
                    final_batches[-1]['records'] += date_group['records']
                elif (
                    date_group['reset'] == 'year'
                    and final_batches[-1]['records'][0].date.year == date_group['records'][0].date.year
                ):
                    final_batches[-1]['records'] += date_group['records']
                else:
                    final_batches += [date_group]

        # Give the name based on previously computed values
        for batch in final_batches:
            for move in batch['records']:
                move.name = batch['format'].format(**batch['format_values'])
                batch['format_values']['seq'] += 1
            batch['records']._compute_split_sequence()

        self.filtered(lambda m: not m.name).name = '/'

    def _constrains_date_sequence(self):
        constraint_date = fields.Date.to_date(self.env['ir.config_parameter'].sudo().get_param(
            'sequence.mixin.constraint_start_date',
            '1970-01-01'
        ))
        for record in self:
            if record.journal_id.usar_secuencia_propia:
                continue
            date = fields.Date.to_date(record[record._sequence_date_field])
            sequence = record[record._sequence_field]
            if sequence and date and date > constraint_date:
                format_values = record._get_sequence_format_param(sequence)[1]
                if (
                    format_values['year'] and format_values['year'] != date.year % 10**len(str(format_values['year']))
                    or format_values['month'] and format_values['month'] != date.month
                ):
                    raise ValidationError(_(
                        "The %(date_field)s (%(date)s) doesn't match the sequence number of the related %(model)s (%(sequence)s)\n"
                        "You will need to clear the %(model)s's %(sequence_field)s to proceed.\n"
                        "In doing so, you might want to resequence your entries in order to maintain a continuous date-based sequence.",
                        date=format_date(self.env, date),
                        sequence=sequence,
                        date_field=record._fields[record._sequence_date_field]._description_string(self.env),
                        sequence_field=record._fields[record._sequence_field]._description_string(self.env),
                        model=self.env['ir.model']._get(record._name).display_name,
                    ))

    def _post(self, soft=True):
        for invoice_id in self:
            if invoice_id.journal_id.usar_secuencia_propia:
                sequence = invoice_id._get_sequence()
                if not sequence:
                    raise UserError('Defina una secuencia en su diario.')
                if len(invoice_id.name.split("-")) < 2:
                    invoice_id.name = sequence.with_context(
                        ir_sequence_date=invoice_id.date).next_by_id()
                    invoice_id.payment_reference = invoice_id.name
            else:
                invoice_id._compute_name()
        return super(AccountMove, self)._post()

    def _get_sequence(self):
        self.ensure_one()
        journal = self.journal_id
        return journal.sequence_id
################################################## FIN  ##########################################################################

##############################################**********************************#####################################
    
    def _search_company(self):
        if self.env.context.get('company_id'):
            company = self.env['res.company'].browse(
                self.env.context['company_id'])
        else:
            company = self.env.company
        return company

    def _json_empresa_envio(self):
        company = self._search_company()
        modo_envio = "1" if company.modo_envio_cpe == 'produccion' else "0"
        empresa_json = {
            'empresa_id' : "1",
            'empresa' : company.partner_id.name,
            'nombre_comercial' : company.partner_id.commercial_name,
            'ruc' : company.vat,
            'domicilio_fiscal' : company.street,
            'telefono_fijo' : company.phone or "",
            'telefono_fijo2' : "",
            'telefono_movil' : company.mobile or "",
            'telefono_movil2' : "",
            'foto' : "",
            'correo' : company.email or "",
            'ubigeo' : company.partner_id.zip,
            'urbanizacion' : "-",
            'usu_secundario_prueba_user' : company.usuario_prueba_cpe,
            'usu_secundario_prueba_passoword' : company.password_prueba_cpe,
            'usu_secundario_produccion_user' : company.usuario_produccion_cpe,
            'usu_secundario_produccion_password' : company.password_produccion_cpe,

            'modo': modo_envio,
            'distrito' : company.partner_id.l10n_pe_district.name or "",
            'provincia' : company.partner_id.city_id.name or "",
            'departamento' : company.partner_id.state_id.name or "",
        }
        empresa_json = json.dumps(empresa_json)
        return empresa_json
    
    def _json_venta_envio(self):
        venta_json = {
            'UBLVersionID' : '2.1'
        }
        venta_json = json.dumps(venta_json)
        return venta_json

    def button_generar_json(self):
        if self.journal_id.is_cpe:
            tipo_vat = self.partner_id.l10n_latam_identification_type_id.name
            fecha_emision = self.invoice_date
            fecha_emision = '%s-%s-%s' % (fecha_emision.day, fecha_emision.month, fecha_emision.year)
            # _logging.info('**************************** Entró a envío: {0}'.format(fecha_emision))
            json_envio = {
                'operacion' : "generar_comprobante",
                'tipo_de_comprobante' : int(self.journal_id.pe_invoice_code),
                'serie' : self.journal_id.code,
                'numero' : int(self.name.split("-")[-1]) ,
                'cliente_tipo_de_documento' : tipo_vat,
                'cliente_numero_de_documento' : self.partner_id.vat,
                'cliente_direccion' : self.partner_id.street,
                'moneda' : self.currency_id.name,
                'fecha_de_emision' : fecha_emision,
            }
            #json_envio['operacion'] = "generar_comprobante"

            json_envio = json.dumps(json_envio)
            self.json_api_envio = json_envio
            _logging.info('**************************** Entró a envío: {0}'.format(json_envio))
            _logging.info('**************************** Entró a empresa envio: {0}'.format(self._json_empresa_envio()))
        else:
            raise UserError(_(
                "El diario seleccionado no permite el envío."
            ))

    def button_envio_sunat(self):
        json_rspt = {
            'error' : False,
            'menssage' : 'Enviado'
        }
        json_rspt = json.dumps(json_rspt)
        self.json_api_rspt = json_rspt
        return json_rspt
        #_logging.info('**************************** Entró a envío: entro a envio de json')
##############################################**********************************#####################################

###############################################QR CODE#####################################################################
    @api.depends('name', 'journal_id.tipo_comprobante.es_cpe', 'journal_id.pe_invoice_code', 'amount_tax', 'amount_total', 'invoice_date', 'partner_id.vat', 'partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code', 'company_id.partner_id.vat','sunat_hash')
    def _compute_get_qr_code(self):
        for invoice in self:
            if not all((invoice.name != '/', invoice.journal_id.tipo_comprobante.es_cpe, qr_mod)):
                invoice.sunat_qr_code = ''
            elif len(invoice.name.split('-')) > 1 and invoice.invoice_date:
                res = [
                    invoice.company_id.partner_id.vat or '-',
                    invoice.journal_id.pe_invoice_code or '',
                    invoice.name.split('-')[0] or '',
                    invoice.name.split('-')[1] or '',
                    str(invoice.amount_tax), 
                    str(invoice.amount_total),
                    fields.Date.to_string(invoice.invoice_date), 
                    invoice.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '-',
                    invoice.partner_id.vat or '-',
                    invoice.sunat_hash or '',
                ]
                qr_string = '|'.join(res)
                _logging.info('**************************** QR SRING: {0}'.format(qr_string))
                qr = qrcode.QRCode(version=1, error_correction=(
                    qrcode.constants.ERROR_CORRECT_Q))
                qr.add_data(qr_string)
                qr.make(fit=True)
                image = qr.make_image()
                tmpf = BytesIO()
                image.save(tmpf, 'png')
                invoice.sunat_qr_code = encodebytes(tmpf.getvalue())
            else:
                invoice.sunat_qr_code = ''

    @api.depends('name', 'journal_id.tipo_comprobante.es_cpe', 'journal_id.pe_invoice_code', 'amount_tax', 'amount_total', 'invoice_date', 'partner_id.vat', 'partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code', 'company_id.partner_id.vat','sunat_hash')
    def _compute_qr_char(self):
        for invoice in self:
            invoice.sunat_qr_code_char = ''
            if not all((invoice.name != '/', invoice.journal_id.tipo_comprobante.es_cpe, qr_mod)):
                invoice.sunat_qr_code_char = ''
            elif len(invoice.name.split('-')) > 1 and invoice.invoice_date:
                res = [
                    invoice.company_id.partner_id.vat or '-',
                    invoice.journal_id.pe_invoice_code or '',
                    invoice.name.split('-')[0] or '',
                    invoice.name.split('-')[1] or '',
                    str(invoice.amount_tax), 
                    str(invoice.amount_total),
                    fields.Date.to_string(invoice.invoice_date), 
                    invoice.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '-',
                    invoice.partner_id.vat or '-',
                    invoice.sunat_hash or '',
                ]

                invoice.sunat_qr_code_char = '|'.join(res)
            return invoice.sunat_qr_code_char
##################################################################$$$$$$$$$$$$$$$$$$$$$###########################