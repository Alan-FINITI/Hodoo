from odoo import api, models, fields, http
import logging

_logger = logging.getLogger(__name__)


class OrderRefuge(models.Model):

    _name = "refuge.order"
    _description = "refuge order online "
    _inherit = "pos.order"

    client_id = fields.Many2one(string="Client id", required=False, comodel_name="refuge.client",
                                inverse_name="order_ids")
    discount = fields.Integer(compute="get_client_discount")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('sent', 'Sent'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft')

    @api.model
    def get_client_discount(self):
        for record in self:
            discount = record.client_id.discount
            record.discount = discount

    def action_next_state(self):
        state_transitions = {
            'draft': 'approved',
            'approved': 'sent',
            'sent': 'done',
            'done': 'done'
        }

        for order in self:
            next_state = state_transitions.get(order.state)
            if next_state:
                order.state = next_state

    def cancel_order(self):
        for order in self:
            order.state = 'cancel'

    @api.onchange("partner_id")
    def add_client(self, client_id):
        for record in self:
            client = self.env['res.partner'].browse(client_id)
            discount_percentage = client.calculate_discount()
            _logger(discount_percentage)
            for line in record.lines:
                line.discount = discount_percentage
