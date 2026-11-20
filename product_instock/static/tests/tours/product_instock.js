import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("product_instock_in_stock_badge", {
    steps: () => [
        {
            content: "The 'I lager' badge is shown for a product in stock",
            trigger: ".availability_messages .badge.text-bg-success:contains('I lager')",
        },
    ],
});

registry.category("web_tour.tours").add("product_instock_no_badge", {
    steps: () => [
        {
            content: "An out of stock product shows no 'I lager' badge",
            trigger:
                ".availability_messages:has(#out_of_stock_message):not(:has(.text-bg-success))",
        },
    ],
});
