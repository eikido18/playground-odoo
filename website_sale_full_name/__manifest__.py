{
    'name': 'Website Sale Full Name',
    'author': 'JH, Claude',
    'version': '20.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Require a first and a last name on the checkout address form',
    'description': """
        On the webshop checkout, the address name must hold both a first name
        and a last name. A single name is refused, and the name input is
        highlighted in red with an explanatory message.
    """,
    'depends': ['website_sale'],
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
