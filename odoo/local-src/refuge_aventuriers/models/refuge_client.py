# from odoo import api, models, fields
#
#
# class RefugeClient(models.Model):
#     _name = "refuge.client"
#     _description = "Client pour l'application web"
#     _inherit_ = "res.partner"
#
#     fidelity_points = fields.Integer(string="Points de fidélité", compute="calculate_fidelity_points")
#     discount = fields.Float(string="Réduction totale", compute="calculate_discount", default=1)
#     order_ids = fields.One2many(string="Order Ids", comodel_name="refuge.order", inverse_name="client_id")
#
#     @api.model
#     def calculate_discount(self):
#         for record in self:
#             if record.fidelity_points >= 1000:
#                 record.discount = 0.80
#                 return 0.80
#             elif record.fidelity_points >= 500:
#                 record.discount = 0.85
#                 return 0.85
#             elif record.fidelity_points >= 200:
#                 record.discount = 0.90
#                 return 0.90
#             elif record.fidelity_points >= 100:
#                 record.discount = 0.95
#                 return 0.95
#
#     def calculate_fidelity_points(self):
#         for record in self:
#             total_points = 0
#             for order in record.order_ids:
#                 total_points += int(order.amount_total)
#             record.fidelity_points = total_points
#
#
#
