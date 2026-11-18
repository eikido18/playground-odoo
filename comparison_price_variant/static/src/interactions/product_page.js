import { patch } from "@web/core/utils/patch";
import { ProductPage } from "@website_sale/interactions/product_page";

patch(ProductPage.prototype, {
    /**
     * Each variant has its own comparison price: update the strikethrough amount
     * and its visibility when the customer picks another combination.
     */
    async _onChangeCombination(ev, parent, combination) {
        const result = await super._onChangeCombination(...arguments);
        const comparePrice = parent.querySelector(".oe_compare_list_price");
        if (comparePrice) {
            const showComparePrice =
                !combination.has_discounted_price &&
                combination.compare_list_price > combination.price;
            comparePrice.classList.toggle("d-none", !showComparePrice);
            const comparePriceValue = comparePrice.querySelector(".oe_currency_value");
            if (showComparePrice && comparePriceValue) {
                comparePriceValue.textContent = this._priceToStr(
                    combination.compare_list_price,
                    combination.currency_precision
                );
            }
        }
        return result;
    },
});
