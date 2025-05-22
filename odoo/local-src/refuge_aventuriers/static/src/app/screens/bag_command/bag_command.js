/** @odoo-module */

import { registry } from "@web/core/registry";
import { useRefuge } from "@refuge_aventuriers/app/store/refuge_hook";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc_service";

// import { usePopup } from "@web/core/popups/popup_service";

export class BagCommandScreen extends Component {
    static template = "refuge_aventuriers.BagCommandScreen";

    setup() {
        this.refuge = useRefuge();
        this.order = null;
        this.currentUser = null;
        this.total = 0;
        this.rpc = useService("rpc");
        console.log(this.props.orderId)
        this.orderId=this.props.orderId
        onMounted(async () => {
            try {
                console.log(this.orderId)
                const order = await this.rpc('/refuge/get_order_info', {
                    order_id: this.orderId
                });



                if (order.error) {
                    console.error("Erreur:", order.error);
                } else {
                    this.order = order;
                    console.log("Commande chargée:", this.order);
                }

                // 2. Récupérer l'utilisateur courant
                const userData = await this.rpc('/refuge/get_current_user_info', {});
                console.log("Utilisateur connecté :", userData);
                this.currentUser = userData;

                // 3. Calcul du total
                this.total = 0;
                this.order.orderlines.forEach(line => {
                    this.total += parseInt(line.quantity) * parseFloat(line.price_unit);
                });
            } catch (e) {
                console.error("Erreur RPC :", e);
            }
        });
    }

    async on_order_button_click(field, value) {
        try {
            await this.refuge.orm.call("refuge.order", "action_next_state", [
                [this.order.id]
            ]);

            await this.refuge.orm.call("refuge.order", "client_update", [
                [this.currentUser.id]
            ]);

            // Optionnel : Popup
            // this.popup.add({...});

        } catch (error) {
            console.error("Erreur lors de l’envoi de la commande :", error);
        }
    }

    async on_change_quantity(productId, newQty) {
        try {
            const quantity = parseInt(newQty, 10);
            if (isNaN(quantity) || quantity < 0) {
                console.warn("Quantité invalide :", newQty);
                return;
            }

            const response = await this.refuge.orm.call("refuge.order", "update_product_quantity", [
                this.order.id,
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
