/** @odoo-module */

import { registry } from "@web/core/registry";
import { Component, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { useRefuge } from "@refuge_aventuriers/app/store/refuge_hook";

export class OnlineOrderScreen extends Component {
    static template = "refuge_aventuriers.OnlineOrderScreen";

    setup() {
        this.allProducts = useState([]);
        this.productsQuantity = {};
        this.orderId = null;
        this.table_number = 1;
        // Structure JS pure pour accumuler les lignes
        this.localOrder = { lines: [] };
        this.rpc = useService("rpc");
        this.refuge = useRefuge();

        onMounted(async () => {
            try {
                // 1. Chargement des produits
                const result = await this.rpc("/refuge_aventuriers/load_refuge_data");
                const products = result["product.template"] || [];
                this.allProducts.splice(0, this.allProducts.length, ...products);
                for (const p of products) {
                    this.productsQuantity[p.id] = 0;
                }

            // 2. Création côté serveur d'une commande vide
            this.orderId = await this.rpc("/refuge_aventuriers/new_order");
            this.localOrder.lines = [];

            } catch (e) {
                console.error("Erreur RPC :", e);
            }
        });
    }

    onQuantityChange(ev) {
        const productId = parseInt(ev.target.id);
        const quantity = parseInt(ev.target.value, 10) || 0;
        this.productsQuantity[productId] = quantity;
    }

    async onViewCart() {
        if (!this.orderId) {
            console.warn("Commande pas encore initialisée !");
            return;
        }
        // Vide les lignes locales
        this.localOrder.lines = [];

        // Construit les lignes à envoyer
        for (const [productId, qty] of Object.entries(this.productsQuantity)) {
            if (qty > 0) {
                this.localOrder.lines.push({
                    product_id: parseInt(productId, 10),
                    quantity: qty,
                });
            }
        }

        if (!this.localOrder.lines.length) {
            console.log("Aucun produit sélectionné.");
            return;
        }
        // Envoi au back
        try {
            await this.rpc("/refuge_aventuriers/update_order", {
                order_id: this.orderId,
                lines: this.localOrder.lines,
                table_number: this.table_number,
            });
            console.info("Commande mise à jour !");
        } catch (e) {
            console.error("Erreur lors de l'envoi de la commande :", e);
        }
    this.refuge.showScreen('BagCommandScreen', {"orderId": this.orderId})
    }
}

registry.category("refuge_screens").add("OnlineOrderScreen", OnlineOrderScreen);
