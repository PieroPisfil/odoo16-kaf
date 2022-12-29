# -*- coding: utf-8 -*-

{
    'name': "kaf-report-base",
    'summary': "Configuraciones para reportes personalizados.",
    'version': '1.1',
    'description': """
       Configuraciones para reportes personalizados.
    """,
    'author': "Piero Pisfil",
    'depends': [
        'contacts',
        'web',
        'stock',
        'sale',
        'kaf-contacts-base',
        'kaf-ticket-base',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'data/report_layout.xml',
        'report/paper_format.xml',
        'report/template_a4_proforma.xml',
        'views/proforma_settings_view.xml',
        'views/res_config_view.xml',
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
