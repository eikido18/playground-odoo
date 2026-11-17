{
    'name': 'Website Sale Full Name',
    'author': 'JH, Claude',
    'version': '20.0.1.1.0',
    'category': 'Website/Website',
    'summary': 'Require a first and a last name at checkout and sign up',
    'description': """
        On the webshop checkout address form and on the sign up page, the name
        must hold both a first name and a last name. A single name is refused,
        and the name input is highlighted in red with an explanatory message.
    """,
    'depends': ['auth_signup', 'website_sale'],
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
