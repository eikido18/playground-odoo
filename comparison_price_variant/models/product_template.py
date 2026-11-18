from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_sales_prices(self, pricelist_sudo, fiscal_position_sudo, website):
        sales_prices = super()._get_sales_prices(pricelist_sudo, fiscal_position_sudo, website)
        if not self.env['res.groups']._is_feature_enabled(
            'website_sale.group_product_price_comparison'
        ):
            return sales_prices

        currency = website.currency_id
        for template in self:
            template_price_vals = sales_prices.get(template.id)
            variant_compare_price = template.product_variant_id.compare_list_price
            if (
                not template_price_vals
                or variant_compare_price == template.compare_list_price
                or template._has_pricelist_base_price(template_price_vals, currency)
            ):
                continue
            if variant_compare_price:
                template_price_vals['base_price'] = template.currency_id._convert(
                    variant_compare_price, currency, self.env.company, round=False
                )
            else:
                template_price_vals.pop('base_price', None)
        return sales_prices

    def _has_pricelist_base_price(self, template_price_vals, currency):
        """Tell whether the `base_price` of the /shop prices comes from a pricelist discount.

        website_sale only falls back on the comparison price when no pricelist
        discount gives a base price, and the pricelist one must be kept.
        """
        self.ensure_one()
        base_price = template_price_vals.get('base_price')
        if base_price is None:
            return False
        if not self.compare_list_price:
            return True
        template_compare_price = self.currency_id._convert(
            self.compare_list_price, currency, self.env.company, round=False
        )
        return currency.compare_amounts(base_price, template_compare_price) != 0

    def _get_additional_combination_info(
        self, product_or_template, quantity, uom, website, pricelist, fiscal_position, **kwargs
    ):
        combination_info = super()._get_additional_combination_info(
            product_or_template, quantity, uom, website, pricelist, fiscal_position, **kwargs
        )
        # website_sale reads the amount on the template; take it from the variant.
        if (
            product_or_template.is_product_variant
            and not combination_info['has_discounted_price']
            and not combination_info['hide_price']
            and self.env['res.groups']._is_feature_enabled(
                'website_sale.group_product_price_comparison'
            )
        ):
            if product_or_template.compare_list_price:
                combination_info['compare_list_price'] = product_or_template.currency_id._convert(
                    from_amount=product_or_template.compare_list_price,
                    to_currency=website.currency_id,
                    round=False,
                )
            else:
                combination_info.pop('compare_list_price', None)
        return combination_info
