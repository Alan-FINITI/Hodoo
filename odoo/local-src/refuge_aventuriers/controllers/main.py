from odoo import http
from odoo.http import request


class RefugeController(http.Controller):

    @http.route(["/refuge/web", "/refuge/ui"], type="http", auth="user")
    def refuge_web(self, **k):
        session_info = request.env["ir.http"].session_info()
        context = {
            "session_info": session_info
        }
        response = request.render("refuge_aventuriers.index", context)
        response.headers["Cache-Control"] = "no-store"
        return response

    @http.route('/refuge_aventuriers/load_refuge_data', type='json', auth='public', csrf=False)
    def load_refuge_data(self):
        return request.env['refuge.management'].load_refuge_data()
    @http.route('/refuge_aventuriers/get_pos_products', type='json', auth='public', csrf=False)
    def get_pos_products(self):
        products = request.env['product.product'].sudo().search([
            ('available_in_pos', '=', True),
            ('sale_ok', '=', True)
        ])
        return [{
            'id': p.id,
            'display_name': p.display_name,
            'lst_price': p.lst_price,
        } for p in products]

    @http.route("/orders/get", type="json", auth="public", csrf=False)
    def get_orders(self, **kwargs):
        orders = request.env["refuge.order"].sudo().search([])

        result = []
        for order in orders:
            result.append({
                "id": order.id,
                "name": order.name,  # hérité de pos.order
                "client_id": order.client_id.id if order.client_id else None,
                "client_name": order.client_id.name if order.client_id else None,
                "discount": order.discount,
                "state": order.state,
                "date_order": order.date_order,  # hérité de pos.order
                "amount_total": order.amount_total,  # hérité de pos.order
            })

        return {"orders": result}
