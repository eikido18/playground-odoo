import json

from odoo.tests import BaseCase, tagged

from odoo.addons.website_sale.tests.common import WebsiteSaleCommon
from odoo.addons.website_sale_full_name.controllers.main import WebsiteSaleFullName, is_full_name


@tagged('post_install', '-at_install')
class TestIsFullName(BaseCase):

    def test_is_full_name(self):
        for name, expected in [
            ('', False),
            ('Jan', False),
            ('  Jan  ', False),
            ('J. Hansen', False),
            ('Jan H.', False),
            ('Jan Hansen', True),
            ('  Jan   Hansen ', True),
            ('Jan Erik Hansen', True),
            ('Åse Ødegård', True),
        ]:
            with self.subTest(name=name):
                self.assertEqual(is_full_name(name), expected)


@tagged('post_install', '-at_install')
class TestCheckoutFullName(WebsiteSaleCommon):

    def setUp(self):
        super().setUp()
        self.controller = WebsiteSaleFullName()
        self.address_values = {
            'email': 'jan@example.com',
            'street': 'Storgatan 1',
            'city': 'Stockholm',
            'zip': '11122',
            'country_id': self.country_be.id,
            'phone': '+46700000000',
            'address_type': 'billing',
        }

    def _submit(self, name):
        order = self._create_so(partner_id=self.env.user.partner_id.id)
        with self.mock_request(sale_order_id=order.id) as req:
            req.httprequest.method = 'POST'
            response = self.controller.shop_address_submit(name=name, **self.address_values)
        return json.loads(response.data)

    def test_single_name_is_refused(self):
        result = self._submit('Jan')
        self.assertIn('name', result['invalid_fields'])
        self.assertIn(
            "Please enter your full first name and last name (e.g. John Smith).",
            result['messages'],
        )

    def test_full_name_is_accepted(self):
        result = self._submit('Jan Hansen')
        self.assertNotIn('invalid_fields', result)
        self.assertIn('redirectUrl', result)
