# -*- coding: utf-8 -*-

{
    'name': "kaf-ticket-base",
    'summary': "Configuraciones para los formatos de ticket.",
    'version': '1.1',
    'description': """
       Agrega el formato ticket para los reportes.
    """,
    'author': "Piero Pisfil",
    'depends': [
        'base',
        'kaf-contacts-base',
    ],
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        # 'data/report_layout.xml',
        'report/ticket_paper_format.xml',
        'report/stock_report_ticket_views.xml',
        # 'views/sale_make_invoice_advance_views.xml',
        # 'views/menu.xml',
        # 'views/datasheet_view.xml',
        # 'views/copier_brand_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
