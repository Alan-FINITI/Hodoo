/** @odoo-module */

import { registry } from "@web/core/registry";
import { Component, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";  // <-- ici

export class OnlineOrderScreen extends Component {
    static template = "refuge_aventuriers.OnlineOrderScreen";

    setup() {
        this.allProducts = useState([]);
        this.rpc = useService("rpc"); // <-- ici

        onMounted(async () => {
            try {
                const result = await this.rpc("/refuge_aventuriers/load_refuge_data");
                // Assure-toi d'accéder aux produits selon ton backend
                this.allProducts.splice(0);
                this.allProducts.push(...(result["product.template"] || []));
            } catch (e) {
                console.error("Erreur RPC :", e);
            }
        });
    }
}

registry.category("refuge_screens").add("OnlineOrderScreen", OnlineOrderScreen);