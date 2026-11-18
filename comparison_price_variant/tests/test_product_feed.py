from odoo.tests import tagged

from odoo.addons.website_sale.tests.common_gmc import WebsiteSaleGMCCommon


@tagged('post_install', '-at_install')
class TestProductFeedCompareListPrice(WebsiteSaleGMCCommon):
    _test_user_groups = (
        'base.group_user',
        'product.group_product_manager',
        'website.group_website_designer',  # product.feed access
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['res.config.settings'].sudo().create({
            'group_product_price_comparison': True,
        }).execute()
        cls.currency_name = cls.website.currency_id.name

    def _gmc_price(self, amount):
        return f"{amount} {self.currency_name}"

    def test_compare_list_price_is_sent_as_price(self):
        self.product_template_sofa.compare_list_price = 1500.0
        self.blue_sofa.compare_list_price = 1300.0

        self.update_items()

        self.assertEqual(self.red_sofa_item['price'], self._gmc_price(1500.0))
        self.assertEqual(self.red_sofa_item['sale_price'], self._gmc_price(1000.0))
        self.assertEqual(self.blue_sofa_item['price'], self._gmc_price(1300.0))
        self.assertEqual(self.blue_sofa_item['sale_price'], self._gmc_price(1200.0))
        self.assertNotIn('sale_price', self.items[self.blanket])

    def test_compare_list_price_below_price_is_ignored(self):
        self.blue_sofa.compare_list_price = 1100.0

        self.update_items()

        self.assertEqual(self.blue_sofa_item['price'], self._gmc_price(1200.0))
        self.assertNotIn('sale_price', self.blue_sofa_item)
