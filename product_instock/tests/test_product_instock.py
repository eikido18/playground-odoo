from odoo.tests import HttpCase, TransactionCase, tagged


class ProductInstockCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env['stock.warehouse'].search(
            [('company_id', '=', cls.env.company.id)], limit=1,
        )
        cls.in_stock_product, cls.out_of_stock_product = cls.env['product.product'].create([
            {
                'name': name,
                'type': 'consu',
                'is_storable': True,
                'allow_out_of_stock_order': False,
                'website_published': True,
            } for name in ("Instock Product", "Outofstock Product")
        ])
        cls.env['stock.quant']._update_available_quantity(
            cls.in_stock_product, cls.warehouse.lot_stock_id, 5,
        )


@tagged('post_install', '-at_install')
class TestProductInstock(ProductInstockCommon):

    def test_is_in_stock(self):
        self.assertTrue(self.in_stock_product.product_tmpl_id.is_in_stock)
        self.assertFalse(self.out_of_stock_product.product_tmpl_id.is_in_stock)


@tagged('post_install', '-at_install')
class TestProductInstockWebsite(HttpCase, ProductInstockCommon):

    def test_in_stock_badge_on_product_page(self):
        if self.env['ir.module.module']._get('website_sale_collect').state == 'installed':
            # Click & Collect replaces the availability widget
            self.env.ref('website.default_website').in_store_dm_id.is_published = False
        self.start_tour(
            self.in_stock_product.website_url, 'product_instock_in_stock_badge', login="",
        )
        self.start_tour(
            self.out_of_stock_product.website_url, 'product_instock_no_badge', login="",
        )
