/** @odoo-module */

import { registry } from "@web/core/registry";
import { useRefuge } from "@refuge_aventuriers/app/store/refuge_hook";
import { Component } from "@odoo/owl";

export class BagCommandScreen extends Component {
    static template = "refuge_aventuriers.BagCommandScreen";
    static props = ["order"];

    setup() {
        if (!this.props.order) {
            console.warn("Aucune commande reçue !");
            this.validOrder = false;
            return;
        }

        this.validOrder = true;
        this.order = this.props.order;
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
async on_change_quantity(productId, newQty) {
    try {
        // Conversion en nombre entier (important pour éviter les erreurs Odoo)
        const quantity = parseInt(newQty, 10);
        if (isNaN(quantity) || quantity < 0) {
            console.warn("Quantité invalide :", newQty);
            return;
        }

        const response = await this.refuge.orm.call("refuge.order", "update_product_quantity", [
            this.lastOrder.id,
            productId,
            quantity
        ]);

        if (response.error) {
            console.error("Erreur Odoo :", response.error);
        } else {
            console.log("Quantité mise à jour :", response.qty);
        }

    } catch (error) {
        console.error("Erreur lors de l’appel RPC :", error);
    }

}
}


registry.category("refuge_screens").add("BagCommandScreen", BagCommandScreen);