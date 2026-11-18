from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.website_sale.tests.common import WebsiteSaleCommon


@tagged('post_install', '-at_install')
class TestVariantCompareListPrice(WebsiteSaleCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['res.config.settings'].create({'group_product_price_comparison': True}).execute()
        size_attribute = cls.env['product.attribute'].create({
            'name': 'Size',
            'value_ids': [Command.create({'name': 'S'}), Command.create({'name': 'L'})],
        })
        cls.template = cls.env['product.template'].create({
            'name': 'Scooter',
            'website_published': True,
            'list_price': 100.0,
            'compare_list_price': 150.0,
            'taxes_id': False,
            'attribute_line_ids': [Command.create({
                'attribute_id': size_attribute.id,
                'value_ids': [Command.set(size_attribute.value_ids.ids)],
            })],
        })
        cls.small_variant, cls.large_variant = cls.template.product_variant_ids

    def _variant_combination_info(self, variant):
        with self.mock_request() as request:
            return variant.with_env(request.env)._get_combination_info_variant()

    def test_variant_follows_template_until_set(self):
        self.assertEqual(self.large_variant.compare_list_price, 150.0)
        self.large_variant.sudo().compare_list_price = 200.0
        self.assertEqual(self.large_variant.compare_list_price, 200.0)
        self.assertEqual(self.small_variant.compare_list_price, 150.0)
        self.assertEqual(self.template.compare_list_price, 150.0)

    def test_combination_info_uses_variant_compare_price(self):
        self.large_variant.sudo().compare_list_price = 200.0
        self.small_variant.sudo().compare_list_price = 0.0
        self.assertEqual(
            self._variant_combination_info(self.large_variant)['compare_list_price'], 200.0
        )
        self.assertNotIn('compare_list_price', self._variant_combination_info(self.small_variant))

    def test_shop_price_uses_first_variant_compare_price(self):
        self.template.product_variant_id.sudo().compare_list_price = 180.0
        with self.mock_request() as request:
            template_price_vals = self.template._get_sales_prices(
                request.pricelist, request.fiscal_position, self.website
            )[self.template.id]
        self.assertEqual(template_price_vals['base_price'], 180.0)
