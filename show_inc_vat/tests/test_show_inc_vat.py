from odoo.tests import tagged

from odoo.addons.website_sale.tests.common import MockRequest, WebsiteSaleCommon


@tagged('post_install', '-at_install')
class TestShowIncVat(WebsiteSaleCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax_25 = cls.env['account.tax'].create({
            'name': 'VAT 25%',
            'amount': 25,
            'amount_type': 'percent',
            'price_include_override': 'tax_excluded',
        })
        cls.template = cls.product.product_tmpl_id
        cls.template.taxes_id = cls.tax_25
        cls.no_taxes = cls.env['account.tax']

    def _price(self, country_code, **kwargs):
        with MockRequest(self.env, website=self.website, country_code=country_code):
            return self.template._apply_taxes_to_price(
                100.0, self.website.currency_id, tax_display='total_included', **kwargs
            )

    def test_norwegian_visitor_sees_vat_despite_fiscal_position(self):
        # Fiscal position maps the 25% VAT away; Norwegian visitors still see it.
        price = self._price('NO', product_taxes=self.tax_25, taxes=self.no_taxes)
        self.assertAlmostEqual(price, 125.0)

    def test_other_visitor_keeps_fiscal_position_mapping(self):
        price = self._price('SE', product_taxes=self.tax_25, taxes=self.no_taxes)
        self.assertAlmostEqual(price, 100.0)

    def test_norwegian_visitor_default_taxes(self):
        # 20.0 callers may omit product_taxes/taxes; defaults must still apply VAT.
        self.assertAlmostEqual(self._price('NO'), 125.0)
