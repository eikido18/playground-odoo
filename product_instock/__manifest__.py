{
    'name': 'Product In Stock Notice',
    'version': '19.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Shows "I lager" indicator on products that are in stock',
    'description': """
        Adds a visual "I lager" (In Stock) heads-up badge on product forms
        and kanban views when the product has available stock.
    """,
    'author': 'Implefy AB',
    'website': 'https://github.com/Implefy-AB/product-instock',
    'license': 'OPL-1',
    'depends': ['website_sale_stock'],
    'data': [
        'views/product_template_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'product_instock/static/src/xml/product_instock.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
