# -*- encoding: utf-8 -*-

{
    'name': 'SDT Inventory Branch Transfer',
    'version': '1.0',
    'category': 'Inventory',
    'author':'Sinergi Data Totalindo, PT',
    'description': """A Inventory Branch Transfer is an instruction to Issued a certain quantity of materials,
                so that they are available at a certain point in another branch to receipt.
    """,
    'summary': 'Create Inventori Transfer between branch',
    'website': 'http://sinergidata.co.id',
    'data': [
        'security/transfer_request_security.xml',
        'security/ir.model.access.csv',
        'data/transfer_request_sequence_data.xml',
        'views/stock_picking_type.xml',
        'views/transfer_request.xml',
        'views/res_company.xml',
        'views/stock_picking.xml',
    ],
    'depends': ['mail','stock','account'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 105,
    'license': 'AGPL-3',
}
