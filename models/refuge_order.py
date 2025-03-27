from odoo import api, models, fields, http
import logging

_logger = logging.getLogger(__name__)


class OrderRefuge(models.Model):
    _name = "refuge.order"
    _description = "refuge order online "


    table_number = fields.integer(string="Table Number", required=True)
    client_id = fields.Many2one(string="Client id", required=False, comodel_name="refuge.client", inverse_name="order_ids")
    product_ids = fields.Many2many(string="Product ids", required=True, comodel_name="product.template")
    amount_total = fields.Float(string="Total amount", compute="compute_total_amount")

    @api.model
    def compute_total_amount(self):
        for record in self:
            amount = 0
            discount = record.client_id.discount
            for product in record.product_ids:
                amount += product.list_price
            record.amount_total = amount*discount

    def get_table_number(self):
        _logger(http.request.httprequest.full_path)

