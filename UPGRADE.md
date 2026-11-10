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
