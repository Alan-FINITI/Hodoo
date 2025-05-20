from odoo import api, fields, models


class RefugeManagement(models.Model):
    _name = "refuge.management"
    _description = "Refuge Management"

    @api.model
    def load_refuge_data(self):
        return {
            # "refuge.order": self.env["refuge.order"].search_read(
            #     fields=["table_number", "client_id", "product_ids", "amount_total"]),
            # "refuge.client": self.env["refuge.client"].search_read(
            #     fields=["fidelity_points", "discount", "order_ids"])
        }
