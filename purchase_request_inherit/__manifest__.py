# -*- encoding: utf-8 -*-

{
    'name': 'Purchase Request Modification',
    'version': '1.0',
    'category': 'Inventory',
    'author':'Sinergi Data Totalindo, PT',
    'description': """A modificatio of purchase request addon.
    """,
    'summary': 'Purchase Request modification',
    'website': 'http://sinergidata.co.id',
    'data': [],
    'depends': ["purchase", "product", "purchase_stock","purchase_request"],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 105,
    'license': 'AGPL-3',
}
