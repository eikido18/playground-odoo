from odoo import models
from odoo.http import request

from odoo.addons.website_sale import utils


class ProductFeed(models.Model):
    _inherit = 'product.feed'

    def _prepare_gmc_price_info(self, product):
        """Send the comparison price as the Google `price` and the actual price as `sale_price`.

        website_sale only fills `sale_price` for pricelist discounts; a comparison price must be
        reported the same way for Google to show the product as on sale. A pricelist discount
        keeps precedence, as on the website.
        """
        price_info = super()._prepare_gmc_price_info(product)
        if not price_info or 'sale_price' in price_info:
            return price_info

        combination_info = self._get_gmc_combination_info(product)
        compare_list_price = combination_info.get('compare_list_price')
        currency = combination_info['currency']
        if (
            compare_list_price
            and currency.compare_amounts(compare_list_price, combination_info['price']) == 1
        ):
            price_info.update({
                'price': utils.gmc_format_price(compare_list_price, currency),
                'sale_price': utils.gmc_format_price(combination_info['price'], currency),
            })
        return price_info

    def _get_gmc_combination_info(self, product):
        # Same call as website_sale's `_prepare_gmc_price_info`, which does not expose its result.
        price_context = product._get_product_price_context(
            product.product_template_attribute_value_ids
        )
        return product.with_context(
            **price_context
        ).product_tmpl_id._get_additional_combination_info(
            product,
            quantity=1.0,
            uom=product.uom_id,
            website=self.website_id,
            pricelist=request.pricelist,
            fiscal_position=request.fiscal_position,
        )
