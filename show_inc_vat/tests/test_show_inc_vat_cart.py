from odoo.fields import Command
from odoo.tests import new_test_user, tagged

from odoo.addons.website_sale.controllers.cart import Cart
from odoo.addons.website_sale.tests.common import WebsiteSaleCommon


@tagged('post_install', '-at_install')
class TestShowIncVatCart(WebsiteSaleCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.CartController = Cart()
        cls.country_no = cls.quick_ref('base.no')
        cls.fpos_no = cls.env['account.fiscal.position'].create({
            'name': 'Export Norway',
            'country_id': cls.country_no.id,
            'company_id': cls.company.id,
            'auto_apply': True,
        })
        cls.tax_25 = cls.env['account.tax'].create({
            'name': 'VAT 25%',
            'amount': 25,
            'amount_type': 'percent',
            'price_include_override': 'tax_excluded',
        })
        cls.tax_0 = cls.env['account.tax'].create({
            'name': 'VAT 0% export',
            'amount': 0,
            'amount_type': 'percent',
            'fiscal_position_ids': [Command.set(cls.fpos_no.ids)],
            'original_tax_ids': [Command.set(cls.tax_25.ids)],
        })
        cls.product.product_tmpl_id.write({
            'list_price': 100.0,
            'taxes_id': [Command.set(cls.tax_25.ids)],
        })
        cls.partner_no = cls.env['res.partner'].create({
            'name': 'Ola Nordmann',
            'street': 'Karl Johans gate 1',
            'city': 'Oslo',
            'zip': '0154',
            'country_id': cls.country_no.id,
            'email': 'ola@example.com',
        })

    def _add_to_cart(self, request):
        self.CartController.add_to_cart(
            product_template_id=self.product.product_tmpl_id.id,
            product_id=self.product.id,
            quantity=1,
        )
        return request.cart

    def _assert_vat_included(self, cart):
        self.assertFalse(cart.fiscal_position_id)
        self.assertEqual(cart.order_line.tax_ids, self.tax_25)
        self.assertAlmostEqual(cart.amount_total, 125.0)

    def _assert_vat_removed(self, cart):
        self.assertEqual(cart.fiscal_position_id, self.fpos_no)
        self.assertEqual(cart.order_line.tax_ids, self.tax_0)
        self.assertAlmostEqual(cart.amount_total, 100.0)
        self.assertFalse(cart.show_inc_vat_fpos_pending)

    def test_norwegian_cart_keeps_vat_until_address_submitted(self):
        with self.mock_request(country_code='NO') as request:
            self.assertEqual(request.fiscal_position, self.fpos_no)
            cart = self._add_to_cart(request)
            self.assertTrue(cart.show_inc_vat_fpos_pending)
            self._assert_vat_included(cart)

            # Address step submitted: the Norwegian address applies the fiscal position.
            cart._update_address(
                self.partner_no.id, {'partner_id', 'partner_invoice_id', 'partner_shipping_id'}
            )
            self._assert_vat_removed(cart)

    def test_norwegian_cart_payment_step_applies_fiscal_position(self):
        # Logged-in customer with a saved Norwegian address who only clicks "Next".
        user = new_test_user(self.env, login='ola_no', groups='base.group_portal')
        user.partner_id.write({
            'country_id': self.country_no.id,
            'street': 'Karl Johans gate 1',
            'city': 'Oslo',
            'zip': '0154',
        })
        with self.mock_request(user=user, country_code='NO') as request:
            cart = self._add_to_cart(request)
            self.assertTrue(cart.show_inc_vat_fpos_pending)
            self._assert_vat_included(cart)

            cart._update_cart_taxes_and_prices()
            self._assert_vat_removed(cart)

    def test_anonymous_norwegian_cart_stays_deferred(self):
        with self.mock_request(country_code='NO') as request:
            cart = self._add_to_cart(request)
            cart._update_cart_taxes_and_prices()
            self.assertTrue(cart.show_inc_vat_fpos_pending)
            self._assert_vat_included(cart)

    def test_other_visitor_cart_not_deferred(self):
        with self.mock_request(country_code='SE') as request:
            cart = self._add_to_cart(request)
            self.assertFalse(cart.show_inc_vat_fpos_pending)
