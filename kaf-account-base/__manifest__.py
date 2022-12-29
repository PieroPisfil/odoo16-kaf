# -*- coding: utf-8 -*-

{
    'name': "kaf-account-base",
    'summary': "Configuraciones iniciales para Facturación Perú",
    'version': '1.1',
    'description': """
       Configuraciones iniciales en el módulo de facturación par poder facturar con sunat.
    """,
    'author': "Piero Pisfil",
    'depends': [
        'kaf-ticket-base',
        'kaf-contacts-base',
        'kaf-report-base',
        'account',
    ],
    'data': [
        'security/pe_datas_security.xml',
        'security/ir.model.access.csv',
        'data/pe_datas.xml',
        'data/tipo_comprobante_pe.xml',
        'report/report_factura_a4.xml',
        'report/report_invoice_ticket.xml',
        'views/account_journal_view.xml',
        'views/account_move_view.xml',
        'views/res_company_view.xml',
        'views/tipo_comprobante_view.xml',
        'views/account_report.xml',
    ],
    # 'assets': {
    #     'point_of_sale.assets': [
    #         'kaf-whatsapp-pos/static/src/js/*',
    #         'kaf-whatsapp-pos/static/src/css/**/*',
    #         'kaf-whatsapp-pos/static/src/js/Screens/**/*',
    #     ],
    #     'web.assets_qweb': [
    #         'kaf-whatsapp-pos/static/src/xml/**',
    #         'kaf-whatsapp-pos/static/src/xml/Screens/**/*',
    #     ],
    # },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
