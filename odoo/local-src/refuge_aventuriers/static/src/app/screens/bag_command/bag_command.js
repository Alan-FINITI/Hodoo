/** @odoo-module */
import { registry } from "@web/core/registry";
import { useRefuge } from "@refuge_aventuriers/app/store/refuge_hook";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useState } from "@odoo/owl";

export class BagCommandScreen extends Component {
    static template = "refuge_aventuriers.BagCommandScreen";

    setup() {
        this.state = useState({
            order: null,
            currentUser: null,
            total: 0,
        });

        this.refuge = useRefuge();
        this.rpc = useService("rpc");

        this.orderId = this.props.orderId;

        onMounted(async () => {
            try {
                const order = await this.rpc('/refuge/get_order_info', {
                    order_id: this.orderId
                });

                if (order.error) {
                    console.error("Erreur:", order.error);
                } else {
                    this.state.order = order;
                }

                const userData = await this.rpc('/refuge/get_current_user_info', {});
                this.state.currentUser = userData;
                console.log(this.state.currentUser)
                this.computeTotal();
                console.log(this.state.total)
            } catch (e) {
                console.error("Erreur RPC :", e);
            }
        });
    }

    computeTotal() {
        if (!this.state.order || !this.state.order.orderlines) return;

        let total = 0;
        this.state.order.orderlines.forEach(line => {
            total += parseInt(line.quantity) * parseFloat(line.price_unit);
        });
        this.state.total = total;
    }

   async on_order_button_click() {
    try {
        // 1) Appel RPC pour passer la commande au next state
        const result = await this.rpc('/refuge/update_order_state', {
            order_id: this.orderId,
        });
        if (result.error) {
            console.error("Erreur serveur :", result.error);
            return;
        }
        // 2) Mettre à jour localement l'état de la commande
        this.state.order.state = result.new_state;
        console.info("Nouvel état :", result.new_state);

        // 3) Appel RPC pour mettre à jour le client si besoin
        const clientResult = await this.rpc('/refuge/update_client_for_order', {
            order_id: this.state.order.id,
            client_id: this.state.currentUser.id,
        });
        if (clientResult.error) {
            console.error("Erreur update client :", clientResult.error);
        }

    } catch (error) {
        console.error("Erreur lors de l’envoi de la commande :", error);
    }
    this.refuge.showScreen('OnlineOrderScreen');
}


    async on_change_quantity(productId, newQty) {
        try {
            const quantity = parseInt(newQty, 10);
            if (isNaN(quantity) || quantity < 0) {
                console.warn("Quantité invalide :", newQty);
                return;
            }

            const response = await this.refuge.orm.call("refuge.order", "update_product_quantity", [
                this.state.order.id,
                productId,
                quantity
            ]);

            if (!response.error) {
                // Met à jour la ligne dans l'état
                const line = this.state.order.orderlines.find(l => l.product_id === productId);
                if (line) {
                    line.quantity = quantity;
                    this.computeTotal(); // Recalcule total
                }
            } else {
                console.error("Erreur Odoo :", response.error);
            }

        } catch (error) {
            console.error("Erreur lors de l’appel RPC :", error);
        }
    }
}

registry.category("refuge_screens").add("BagCommandScreen", BagCommandScreen);