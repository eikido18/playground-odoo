from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    show_inc_vat_fpos_pending = fields.Boolean(
        string="Fiscal Position Deferred",
        copy=False,
        help="Set on carts of Norwegian (GeoIP) visitors: the fiscal position is not applied, "
             "so prices keep the VAT, until the customer confirms an address in the checkout.",
    )

    def _apply_deferred_fiscal_position(self):
        """Apply the fiscal position of the order address and recompute the taxes, for carts
        created with a deferred fiscal position."""
        for order in self.filtered('show_inc_vat_fpos_pending'):
            if order._is_anonymous_cart():
                # No real address yet: keep showing the VAT.
                continue
            order.show_inc_vat_fpos_pending = False
            fpos_before = order.fiscal_position_id
            order._compute_fiscal_position_id()
            if order.fiscal_position_id != fpos_before:
                order._recompute_taxes()

    def _update_address(self, partner_id, fnames=None):
        res = super()._update_address(partner_id, fnames)
        if fnames:
            self._apply_deferred_fiscal_position()
        return res

    def _update_cart_taxes_and_prices(self, **kwargs):
        # Safety net on the payment step (e.g. a logged-in customer who kept a
        # saved address): never pay a cart with the fiscal position deferred.
        self._apply_deferred_fiscal_position()
        return super()._update_cart_taxes_and_prices(**kwargs)
