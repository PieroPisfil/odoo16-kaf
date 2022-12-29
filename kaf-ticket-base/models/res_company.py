# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    kaf_ticket_layout_id = fields.Many2one('ir.ui.view', 'Document Plantilla de ticket', default='')