# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ArchivoVenta(models.Model):
    _name = "archivo.venta"
    _inherit = ['image.mixin']

    name = fields.Char(string='Nombre',copy=False,index=True, required=True, states={'borrador': [('readonly', False)]}, default=lambda self: _('Nuevo'))
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('proforma', 'Proforma'),
        ('venta', 'Venta Hecha'),
        ('desechado', 'Desechado'),
    ], default='borrador', string='Estado', readonly=True, copy=False, index=True, tracking=3)
    partner_id_principal = fields.Many2one(
        comodel_name='res.partner',
        string='Contacto Principal', required=True, readonly=True,
        states={'borrador': [('readonly', False)], 'proforma': [('readonly', False)]},
        change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    partner_ids_secundarios = fields.Many2many(
        comodel_name='res.partner',
        string='Contactos que pertenecen a este archivo',required=False)
    fotocopiadora_id = fields.Many2one(
        comodel_name='product.template',
        string='Modelo Fotocopiadora')
    suministros_id = fields.Many2many(
        comodel_name='product.template',
        string='Productos Adicionales para compra'
    )
    forma_de_pago_pe = fields.Selection([
        ('contado','CONTADO'),
        ('credito','CRÉDITO')
    ],string="Forma de Pago", default="contado", copy=False, required=True)
    fch_aprobado = fields.Datetime(string='Fecha aprobado', copy=False)
    active = fields.Boolean(default=True)