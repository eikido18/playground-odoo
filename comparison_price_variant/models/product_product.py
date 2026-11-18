from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Shadows the template field reached through `_inherits` so that every
    # `product_or_template.compare_list_price` read in website_sale gets the
    # variant value; mirrors how `lst_price` relates to `list_price`.
    compare_list_price = fields.Monetary(
        string="Compare to Price",
        compute='_compute_compare_list_price',
        inverse='_inverse_compare_list_price',
        store=True,
        readonly=False,
        help="Strikethrough price shown on the /shop and product pages for this variant, for "
        "comparison purposes. It follows the product's Compare to Price until it is set here. "
        "It will not be displayed if pricelists apply.",
    )

    @api.depends('product_tmpl_id.compare_list_price')
    def _compute_compare_list_price(self):
        for product in self:
            product.compare_list_price = product.product_tmpl_id.compare_list_price

    def _inverse_compare_list_price(self):
        for product in self:
            template = product.product_tmpl_id
            if (
                len(template.with_context(active_test=False).product_variant_ids) == 1
                and not template.has_configurable_attributes
            ):
                template.compare_list_price = product.compare_list_price
