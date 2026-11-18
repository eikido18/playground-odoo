{
    'name': 'Comparison Price Variant',
    'author': 'JH, Claude',
    'version': '20.0.1.1.0',
    'category': 'Website/Website',
    'summary': 'Comparison (strikethrough) price per product variant',
    'description': """
        The "Comparison price" setting adds a strikethrough "Compare to Price" on
        the product template. This module lets each product variant carry its own
        comparison price, the same way each variant carries its own sales price.

        The variant comparison price follows the template one until it is set on
        the variant. It is shown as the strikethrough price on the /shop grid, on
        the product page (updated when another variant is picked), in product
        snippets such as the products carousel, and in the product comparison.

        In the Google Merchant Center product feeds, a comparison price above the
        actual price is sent as the "price", with the actual price as the
        "sale_price", the same way pricelist discounts are reported.
    """,
    'depends': ['website_sale'],
    'data': [
        'views/product_views.xml',
        'views/product_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'comparison_price_variant/static/src/interactions/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
