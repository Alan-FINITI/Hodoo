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

    @http.route('/refuge_aventuriers/new_order', type='json', auth='public', csrf=False)
    def new_order(self, product_id=None):
        session = request.env['pos.session'].sudo().search([('state', '=', 'opened')], limit=1)
        if not session:
            return {'error': 'Aucune session POS ouverte.'}

        seq_obj = session.config_id.sequence_id
        if not seq_obj:
            return {'error': 'Pas de séquence configurée sur cette session POS.'}
        seq = seq_obj.next_by_id()

        order_vals = {
            'session_id': session.id,
            'company_id': session.company_id.id,
            'pricelist_id': session.config_id.pricelist_id.id,
            'user_id': request.env.uid,
            'name': seq,
            'pos_reference': seq,
            'state': 'draft',
            'amount_tax': 0.0,
            'amount_total': 0.0,
            'amount_paid': 0.0,
            'amount_return': 0.0,
            'to_invoice': False,
        }

        new_order = request.env['pos.order'].sudo().create(order_vals)

        if product_id:
            product = request.env['product.product'].sudo().browse(product_id)
            if product.exists():
                line_vals = {
                    'order_id': new_order.id,
                    'product_id': product.id,
                    'qty': 1,
                    'price_unit': product.lst_price,
                    'full_product_name': product.display_name,  # Nom complet du produit
                }
                request.env['pos.order.line'].sudo().create(line_vals)

        return new_order.id

    @http.route('/refuge_aventuriers/update_order', type='json', auth='public', csrf=False)
    def update_order(self, order_id, lines):
        Order = request.env['pos.order'].sudo().browse(int(order_id))
        if not Order.exists():
            return {'error': 'Commande introuvable.'}
        if Order.state != 'draft':
            return {'error': 'La commande doit être en état draft pour être modifiée.'}

        # 1) Supprimer toutes les lignes existantes
        request.env['pos.order.line'].sudo().search([('order_id', '=', Order.id)]).unlink()

        # 2) Créer les nouvelles lignes
        Product = request.env['product.product'].sudo()
        new_count = 0
        total_ttc = 0.0  # Total TTC pour calculer amount_total

        for line in lines:
            prod_id = int(line.get('product_id', 0))
            qty = float(line.get('quantity', 0))
            if qty <= 0:
                continue

            prod = Product.browse(prod_id)
            if not prod.exists():
                continue

            # Prix unitaire et remise
            price_unit = prod.lst_price
            discount = 0.0

            # Calcul du subtotal HT
            price_subtotal = qty * price_unit * (1 - discount / 100.0)

            # Taxes
            taxes = prod.taxes_id.filtered(lambda t: t.company_id == Order.company_id)

            price_subtotal_incl = price_subtotal
            for tax in taxes:
                tax_value = tax._compute_amount(price_subtotal, price_unit, qty)
                price_subtotal_incl += tax_value

            # Ajout au total de la commande
            total_ttc += price_subtotal_incl

            # Nom de la ligne = nom complet du produit
            line_name = prod.display_name

            # Création de la ligne POS
            request.env['pos.order.line'].sudo().create({
                'order_id': Order.id,
                'product_id': prod.id,
                'qty': qty,
                'price_unit': price_unit,
                'discount': discount,
                'price_subtotal': price_subtotal,
                'price_subtotal_incl': price_subtotal_incl,
                'name': line_name,
            })
            new_count += 1

        # 3) Mise à jour du total de la commande
        Order.write({
            'amount_total': total_ttc
        })

        return {
            'success': True,
            'order_id': Order.id,
            'lines_count': new_count,
            'total': total_ttc,
        }


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

    @http.route('/refuge/get_current_user_info', type='json', auth='user')
    def get_current_user_info(self):
        user = request.env.user
        return {
            # 'user_id': user.id,
            'partner_id': user.partner_id.id,
            # 'name': user.name,
            # 'email': user.email,
        }

    @http.route('/refuge/get_order_info', type='json', auth='user')
    def get_order_info(self, order_id=None):
        if not order_id:
            return {'error': 'Missing order_id'}

        order = request.env['pos.order'].sudo().browse(order_id)
        if not order.exists():
            return {'error': 'Order not found'}

        return {
            'id': order.id,
            'contact_id': order.partner_id.id if order.partner_id else None,
            'client_name': order.partner_id.name if order.partner_id else "Client anonyme",
            'amount_total': order.amount_total,
            'orderlines': [{
                'id': line.id,
                'product': {
                    'id': line.product_id.id,
                    'display_name': line.product_id.display_name,
                },
                'quantity': line.qty,
                'price_unit': line.price_unit,
                'price_display': line.price_subtotal,
            } for line in order.lines],
        }
