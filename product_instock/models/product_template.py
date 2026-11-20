from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_in_stock = fields.Boolean(
        string='I lager',
        compute='_compute_is_in_stock',
        store=False,
    )

    @api.depends('qty_available')
    def _compute_is_in_stock(self):
        for product in self:
            product.is_in_stock = product.qty_available > 0
