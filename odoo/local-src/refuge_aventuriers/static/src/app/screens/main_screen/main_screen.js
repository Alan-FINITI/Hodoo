/** @odoo-module */

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useRefuge } from "@refuge_aventuriers/app/store/refuge_hook";


export class MainScreen extends Component {
    static template = "refuge_aventuriers.MainScreen";

    setup() {
        this.refuge = useRefuge();
        this.lastOrder = null;
    }
    async openBagCommandScreen() {
const [lastOrder] = await this.orm.searchRead("refuge.order", [], [
        'name',
        'client_id',
        'order_line_ids',
        'amount_total'
    ], 0, 1, 'id desc');

    if (lastOrder) {
        this.lastOrder = lastOrder;
        if (lastOrder) {
            this.showScreen("BagCommandScreen", { order: lastOrder });
    } else {
        this.showScreen("BagCommandScreen", { order: null }); }
    } else {
        console.warn("Aucune commande trouvée.");
    }
}
}

registry.category("refuge_screens").add("MainScreen", MainScreen);