from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class OrderRefuge(models.Model):
    _inherit = "pos.order"
    _description = "Refuge order online"

    client_id = fields.Many2one(
        comodel_name="refuge.client",
        string="Client",
    )
    client_id = fields.Many2one(
        comodel_name="refuge.client",
        string="Client",
    )
    discount = fields.Float(
        string="Client Discount (%)",
        compute="_compute_client_discount",
        store=True,
    )
    state = fields.Selection([
        ('draft',     'Draft'),
        ('approved',  'Approved'),
        ('sent',      'Sent'),
        ('done',      'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    table_number = fields.Integer(string="Numéro de table", default=1)
    @api.model
    def update_table_number(self, tableNumber):
        for record in self:
            record.table_number = tableNumber
    @api.depends('client_id.discount')
    def _compute_client_discount(self):
        for order in self:
            order.discount = order.client_id.discount or 0.0

    def action_next_state(self):
        transitions = {
            'draft':    'approved',
            'approved': 'sent',
            'sent':     'done',
            'done':     'done',
        }
        for order in self:
            order.state = transitions.get(order.state, order.state)

    def cancel_order(self):
        for order in self:
            order.state = 'cancelled'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for order in self:
            discount = order.partner_id.calculate_discount() if order.partner_id else 0.0
            for line in order.order_line:
                line.discount = discount
            _logger.info(
                "Applied discount %s%% for partner %s on order %s",
                discount, order.partner_id, order.name
            )

    @api.model
    def update_product_quantity(self, order_id, product_id, quantity):
        order = self.browse(int(order_id))
        if not order:
            return {'error': 'Order not found'}
        line = order.order_line.filtered(lambda l: l.product_id.id == int(product_id))
        if not line:
            return {'error': 'Product not found in order'}
        line.qty = float(quantity)
        # Si nécessaire, recompute subtotal ici...
        return {
            'success':  True,
            'line_id':  line.id,
            'quantity': line.qty,
            'subtotal': line.price_subtotal,
        }

    @api.model
    def client_update(self, clientId):
        for record in self:
            client_id = clientId

    @api.model
    def get_client_discount(self):
        for record in self:
            discount = record.client_id.discount
            record.discount = discount

    @api.model
    def get_command_by_ID(self, order_id):
        order = self.browse(order_id)
        if not order.exists():
            return {'error': 'Order not found'}

        lines = []
        for line in order.lines:
            image_url = '/web/image/product.product/{}/image_1920'.format(line.product_id.id)
            lines.append({
                'product_id': line.product_id.id,
                'product_name': line.product_id.name,
                'qty': line.qty,
                'price_unit': line.price_unit,
                'discount': line.discount,
                'image_url': image_url,
            })

        result = order.read(['id', 'partner_id', 'state', 'table_number'])[0]
        result['lines'] = lines
        return result
