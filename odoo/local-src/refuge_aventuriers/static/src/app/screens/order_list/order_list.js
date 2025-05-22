/** @odoo-module **/

import { Component, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class OrderListScreen extends Component {
    static template = "refuge_aventuriers.OrderListScreen";

    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            orders: [],
            currentScreen: "list",
            selectedOrder: null,
        });

        onMounted(async () => {
            const result = await this.rpc("/orders/get");
            this.state.orders = result.orders;
        });
    }

    async showOrderDetails(orderId) {
        const result = await this.rpc("/orders/details", { order_id: orderId });
        this.state.selectedOrder = result;
        this.state.currentScreen = "details";
    }

    goBack() {
        this.state.currentScreen = "list";
        this.state.selectedOrder = null;
    }
}
registry.category("refuge_screens").add("OrderListScreen", OrderListScreen);