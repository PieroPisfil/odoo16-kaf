# -*- coding: utf-8 -*-

{
    'name': "kaf-contacts-base",
    'summary': "Auto-completa datos de contactos usando una api de búsqueda según DNI o RUC",
    'version': '1.1',
    'description': """
       Se quiere agregar campos para el modulo de contactos según Perú desde módulo Contactos o POS
    """,
    'author': "Piero Pisfil",
    'depends': [
        'base',
        'contacts',
        'l10n_pe',
        'l10n_latam_base',
        'point_of_sale',
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
        'data/res_country_data.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
    #         'kaf-contacts-base/static/src/js/models.js',
    #         'kaf-contacts-base/static/src/js/Screens/**/*',
    #         'kaf-contacts-base/static/src/js/Screens/PartnerListSrceen/*',
            'kaf-contacts-base/static/src/js/models.js',
            'kaf-contacts-base/static/src/js/Screens/PartnerListScreen/PartnerDetailsEdit.js',
            'kaf-contacts-base/static/src/xml/Screens/PartnerListScreen/PartnerDetailsEdit.xml',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
