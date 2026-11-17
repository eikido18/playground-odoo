from odoo import http
from odoo.http import request

from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.website_sale.controllers.main import WebsiteSale

MIN_NAME_PART_LETTERS = 2


def is_full_name(name):
    """Return whether `name` holds a first and a last name.

    The name needs at least two words, and its first and last words must each
    contain at least `MIN_NAME_PART_LETTERS` letters, so that a lone initial
    ("J. Hansen") is not accepted as a first name.
    """
    parts = (name or '').split()
    if len(parts) < 2:
        return False
    return all(
        sum(char.isalpha() for char in part) >= MIN_NAME_PART_LETTERS
        for part in (parts[0], parts[-1])
    )


def full_name_error(env):
    return env._("Please enter your full first name and last name (e.g. John Smith).")


class WebsiteSaleFullName(WebsiteSale):

    def _validate_address_values(
        self,
        address_values,
        partner_sudo,
        address_type,
        use_delivery_as_billing,
        required_fields,
        **kwargs,
    ):
        """Override of `portal` to require a first and a last name on checkout addresses."""
        invalid_fields, missing_fields, error_messages = super()._validate_address_values(
            address_values,
            partner_sudo,
            address_type,
            use_delivery_as_billing,
            required_fields,
            **kwargs,
        )
        if (
            kwargs.get('order_sudo')  # Only on the shop checkout, not on /my/addresses.
            and address_values.get('name')  # An empty name is already reported as missing.
            and 'name' not in invalid_fields
            and not is_full_name(address_values['name'])
        ):
            invalid_fields.add('name')
            error_messages.append(full_name_error(self.env))
        return invalid_fields, missing_fields, error_messages


class AuthSignupFullName(AuthSignupHome):

    @http.route()
    def web_auth_signup(self, *args, **kw):
        """Override of `auth_signup` to require a first and a last name on the sign up page.

        The flag scopes the check to this page: `get_auth_signup_qcontext` is shared with the
        password reset, which must keep working for accounts whose name is a single word.
        """
        request.update_context(signup_require_full_name=True)
        return super().web_auth_signup(*args, **kw)

    def get_auth_signup_qcontext(self):
        """Override of `auth_signup` to refuse a sign up whose name is not a full name.

        An `error` in the rendering context makes `web_auth_signup` skip the account creation
        and render the form again, with the message in its error box.
        """
        qcontext = super().get_auth_signup_qcontext()
        if (
            request.env.context.get('signup_require_full_name')
            and request.httprequest.method == 'POST'
            and 'error' not in qcontext
            and not is_full_name(qcontext.get('name'))
        ):
            qcontext['error'] = full_name_error(request.env)
            qcontext['invalid_name'] = True
        return qcontext
