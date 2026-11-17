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
            error_messages.append(self.env._(
                "Please enter your full first name and last name (e.g. John Smith)."
            ))
        return invalid_fields, missing_fields, error_messages
