# Upgrade 19.0 -> 20.0

## show_inc_vat

### Technical summary
- Manifest version bumped to `20.0.1.0.0`.
- No XML in the module; `odev upgrade-code --from 19.0 --to 20.0` produced no changes.
- `product.template._apply_taxes_to_price` override rewritten for the new signature:
  - 19.0: `(price, currency, product_taxes, taxes, product_or_template, website=None)` (all positional, `@api.model`).
  - 20.0: `(price, currency, *, product=None, product_taxes=None, taxes=None, tax_display=None, website=None)`;
    `product_taxes` defaults to the template taxes filtered by company, `taxes` to
    `request.fiscal_position.map_tax(product_taxes)`.
  - The override keeps its business rule: for GeoIP-Norwegian visitors, `taxes` is forced to
    `product_taxes` (computing the website_sale default when omitted), so prices show 25% VAT;
    checkout still uses the fiscal position.
- Added `tests/test_show_inc_vat.py` (post_install).

### Odoo sources
| Breaking change | Odoo commit |
| --- | --- |
| `_apply_taxes_to_price` keyword-only args with defaults | [odoo/odoo@5d051643aadc](https://github.com/odoo/odoo/commit/5d051643aadc4aa350d8bb318c933e7f5fcb9265) (odoo/odoo#263605) |

`request.geoip` is unchanged in 20.0 (`odoo/http/geoip.py`). The country check now uses
`request.geoip.country_code` (as core website_sale does) instead of `if geoip` truthiness:
`GeoIP.__bool__` is `country_name is not None`, so a record without a localized name
silently skipped the Norwegian rule (pre-existing in 19.0, exposed by the new tests).

Tests: `odev test -V 20.0 <fresh_db> -i show_inc_vat -t /show_inc_vat` -> 0 failed, 0 errors.

### Functional test scenarios
1. Configure a fiscal position (auto-apply, country Norway) that maps the 25% VAT away.
2. Browse `/shop` as a public visitor from a Norwegian IP: product prices show **incl. 25% VAT**.
3. Browse from another country (e.g. Sweden) with a similar fiscal position: prices show **without** VAT.
4. As the Norwegian visitor, add to cart and checkout: the order uses the fiscal position (no VAT charged).
5. Product page with variants/configurator: extra prices follow the same rule.

## product_instock

### Technical summary
- Manifest version bumped to `20.0.1.0.0` (module was imported as-is from 19.0 first, commit `[ADD]`).
- `odoo-bin upgrade_code --from 19.0 --to 20.0`: the frontend badge icon `fa fa-circle` became
  `<i class="oi oi-filled" data-icon="circle"/>` (script `19.5-00-material-symbols-icons`).
  Note: with the 20.0 venv (Python 3.12) the glob must be `product_instock/**/*`;
  `product_instock/**` only matches directories and silently changes nothing.
- Frontend QWeb extension retargeted from `website_sale_stock.product_availability` (removed) to
  `website_sale.product_availability`. Expressions now read `this.free_qty` / `this.product_template`,
  as the core template does. The badge is still inserted after `#threshold_message`, inside the
  `is_storable and !prevent_sale` guard.
- Backend form/kanban views and the `is_in_stock` compute (`qty_available`) are unchanged: their
  anchors (`button_box`, `t-name="card"`) still exist in 20.0.
- Added `tests/test_product_instock.py` (compute test + `product_instock_*` tours) and the
  `web.assets_tests` entry.

### Odoo sources
| Breaking change | Odoo commit |
| --- | --- |
| `website_sale_stock.product_availability` removed, availability moved to `website_sale.product_availability` | [odoo/odoo@2378d9d5b4f6](https://github.com/odoo/odoo/commit/2378d9d5b4f60300d0c7d00558d8e8c71f9b01eb) (odoo/odoo#256137) |
| FontAwesome replaced by Material Symbols (`oi` + `data-icon`) | `odoo/upgrade_code/19.5-00-material-symbols-icons.py` |

Tests: `odev test -c -V 20.0 <fresh_db> -i product_instock -t /product_instock` -> 0 failed, 0 errors.
The tour was **skipped** in the upgrade sandbox (headless Chrome missing `libatk-1.0.so.0`); the
inheritance was checked instead by applying the xpath to the 20.0 parent template and by confirming
`web.assets_frontend` builds with `product_instock.in_stock_badge`. Run the tour where Chrome works.

### Functional test scenarios
1. Backend: open a storable product with on-hand quantity > 0: the green **I lager** badge shows in the
   form (button box area) and on its kanban card; with 0 on hand, no badge.
2. Website: open the product page of a storable, published product with free quantity > 0: the
   **I lager** badge shows under the availability messages.
3. Set "Show available qty" with a threshold above the stock: the threshold badge and **I lager** both show.
4. Product with 0 free quantity and out-of-stock orders disallowed: "Out of Stock" shows, no **I lager**.
5. Product with variants: switching to an out-of-stock variant hides the badge; switching back shows it.
