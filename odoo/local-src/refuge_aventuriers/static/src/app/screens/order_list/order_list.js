/** @odoo-module */

import { registry } from "@web/core/registry";
import { useRefuge } from "@refuge_aventuriers/app/store/refuge_hook";
import { Component } from "@odoo/owl";
import { useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class OrderListScreen extends Component {
    static template = "refuge_aventuriers.OnlineOrderScreen";

    setup() {
    this.state = useState({
        currentScreen: "list",
        orders: [],
        products: [],
    });

    this.rpc = useService("rpc");

    this.loadOrders();
}

    async loadOrders() {
        const result = await this.rpc("/orders/get");
        this.state.orders = result;
    }

//    async showOrderDetails(orderId) {
//        const result = await this.rpc("/orders/details", { order_id: orderId });
//        this.state.products = result;
//        this.state.currentScreen = "details";
//    }

    goBack() {
        this.state.currentScreen = "list";
    }

//    get CurrentScreen() {
//        return this.state.currentScreen === "list"
//            ? OrderListScreen
//            : OrderDetailScreen;
//    }

//    static template = "OrderApp";

    static components = {
        OrderListScreen,
//        OrderDetailScreen,
    };

    static props = {};
}

registry.category("refuge_screens").add("OrderListScreen", OrderListScreen);