from odoo import models

from odoo.addons.show_inc_vat.tools import is_norwegian_visitor


class Website(models.Model):
    _inherit = 'website'

    def _prepare_sale_order_values(self, partner_sudo):
        values = super()._prepare_sale_order_values(partner_sudo)
        if is_norwegian_visitor():
            # Keep the VAT on the cart lines until the customer has confirmed
            # an address; the fiscal position is applied at that point.
            values['fiscal_position_id'] = False
            values['show_inc_vat_fpos_pending'] = True
        return values
