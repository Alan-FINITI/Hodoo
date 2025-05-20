/** @odoo-module */

import { registry } from "@web/core/registry";
import { useRefuge } from "@refuge_aventuriers/app/store/refuge_hook";
import { Component } from "@odoo/owl";

export class OnlineOrderScreen extends Component {
    static template = "refuge_aventuriers.OnlineOrderScreen";

    setup() {
        this.refuge = useRefuge();
    }


    onInput(ev, field) {
        this.props.order[field] = ev.target.value;
        this.refuge.orm.call("refuge.order", "write", [this.props.order.id, this.props.order])
    }

//    on_order_button_click(field, value){
//    this.refuge.orm.call("refuge.order", "write", [
//                this.props.order.id,
//                {
//                    state: "Envoyé",
//                }
//            ]);
//    }


}

registry.category("refuge_screens").add("OnlineOrderScreen", OnlineOrderScreen);