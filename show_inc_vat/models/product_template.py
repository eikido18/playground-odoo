from odoo import models
from odoo.http import request


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _apply_taxes_to_price(self, price, currency, product_taxes, taxes, product_or_template, website=None):
        # For Norwegian visitors (GeoIP), ignore fiscal position tax mapping
        # so they see prices inc. 25% VAT and can compare with Norwegian webshops.
        # The pricelist price is already resolved before this method is called,
        # so Norwegian visitors still see their own pricelist prices.
        geoip = getattr(request, 'geoip', None) if request else None
        country = getattr(geoip, 'country', None) if geoip else None
        if country and getattr(country, 'iso_code', None) == 'NO':
            taxes = product_taxes
        return super()._apply_taxes_to_price(
            price, currency, product_taxes, taxes, product_or_template, website
        )
