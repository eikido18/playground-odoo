import json
from unittest.mock import patch

from odoo.tests import BaseCase, HttpCase, tagged

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


@tagged('post_install', '-at_install')
class TestSignupFullName(HttpCase):

    def setUp(self):
        super().setUp()
        self.env['ir.config_parameter'].sudo().set_str('auth_signup.invitation_scope', 'b2c')
        # The captcha is not what is tested here.
        captcha_patcher = patch.object(
            self.env.registry['ir.http'], '_verify_request_recaptcha_token', lambda *args: None
        )
        captcha_patcher.start()
        self.addCleanup(captcha_patcher.stop)

    def _signup(self, name, login):
        self.authenticate(None, None)
        return self.url_open('/web/signup', data={
            'name': name,
            'login': login,
            'password': 'a-long-password',
            'confirm_password': 'a-long-password',
            'csrf_token': self.csrf_token(),
        })

    def test_single_name_is_refused(self):
        response = self._signup('Jan', 'jan.single@example.com')
        self.assertIn(
            "Please enter your full first name and last name (e.g. John Smith).", response.text
        )
        self.assertIn('is-invalid', response.text)
        self.assertFalse(self.env['res.users'].search([('login', '=', 'jan.single@example.com')]))

    def test_full_name_is_accepted(self):
        response = self._signup('Jan Hansen', 'jan.hansen@example.com')
        self.assertNotIn("Please enter your full first name and last name", response.text)
        self.assertTrue(self.env['res.users'].search([('login', '=', 'jan.hansen@example.com')]))
