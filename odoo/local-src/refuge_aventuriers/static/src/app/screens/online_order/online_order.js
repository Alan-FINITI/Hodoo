/** @odoo-module */

import { registry } from "@web/core/registry";
import { Component, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class OnlineOrderScreen extends Component {
    static template = "refuge_aventuriers.OnlineOrderScreen";

    setup() {
        this.allProducts = useState([]);
        this.rpc = useService("rpc");
        this.productsQuantity = {};
        this.order = null;
        this.orderId = null;

        onMounted(async () => {
            try {
                const result = await this.rpc("/refuge_aventuriers/load_refuge_data");
                const products = result["product.template"] || [];

                this.allProducts.splice(0);
                this.allProducts.push(...products);

                for (const product of products) {
                    this.productsQuantity[product.id] = 0;
                }

                const order = await this.rpc("/refuge_aventuriers/new_order");
                this.order = order;
                this.orderId = order.id;
                this.order.lines = []; // on initialise une liste de lignes
            } catch (e) {
                console.error("Erreur RPC :", e);
            }
        });
    }

    onQuantityChange(ev) {
        const productId = parseInt(ev.target.closest("tr").dataset.productId);
        const quantity = parseInt(ev.target.value) || 0;
        this.productsQuantity[productId] = quantity;
        console.log(this.productsQuantity)
    }


    async on_view_cart() {
        let hasProduct = false;
        this.order.lines = []; // Réinitialise les lignes de commande

        for (const [productId, quantity] of Object.entries(this.productsQuantity)) {
            if (quantity > 0) {
                hasProduct = true;
                // Ajouter le produit et la quantité à la commande
                this.order.lines.push({
                    product_id: parseInt(productId),
                    quantity: quantity,
                });
            }
        }

        if (!hasProduct) {
            refuge.showScreen('BagCommandScreen', this.orderId);
        } else {
            try {
                // Envoyer la commande au serveur
                await this.rpc("/refuge_aventuriers/update_order", {
                    order_id: this.orderId,
                    lines: this.order.lines,
                });
            } catch (e) {
                console.error("Erreur lors de l'envoi de la commande :", e);
            }

            refuge.showScreen('BagCommandScreen', this.orderId);
        }
    }
}

registry.category("refuge_screens").add("OnlineOrderScreen", OnlineOrderScreen);
