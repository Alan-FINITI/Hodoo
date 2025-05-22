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
    def new_order(self):
        PosOrder = request.env['pos.order'].sudo()
        Product = request.env['product.product'].sudo()
        PosSession = request.env['pos.session'].sudo()
        # Récupérer la session POS active
        active_session = PosSession.search([('state', '=', 'opened')], limit=1)
        # if not active_session:
        #     return {
        #         'error': 'No active POS session found.',
        #     }
        # # Préparer les lignes de commande avec une ligne de base vide
        # order_lines = []
        # generic_product = Product.search([], limit=1)  # Juste obtenir un produit disponible
        # if generic_product:
        #     order_lines = [(0, 0, {
        #         'product_id': generic_product.id,
        #         'qty': 0,
        #         'price_unit': 0.0,
        #         'discount': 0,
        #     })]
        order_vals = {
            'session_id': active_session.id,
            'company_id': active_session.company_id.id,
            'amount_tax': 0.0,
            'amount_total': 0.0,
            'amount_paid': 0.0,
            'amount_return': 0.0,
            'state': 'draft',  # important si pas défini par défaut
            'pricelist_id': active_session.config_id.pricelist_id.id,  # souvent obligatoire
            'fiscal_position_id': None,  # facultatif si pas géré
            'user_id': request.env.uid,
        }

        new_order = PosOrder.create(order_vals)

        return new_order

    @http.route('/refuge_aventuriers/update_order', type='json', auth='public', csrf=False)
    def update_order(self, order_id, lines):
        Order = request.env['pos.order'].sudo().browse(int(order_id))
        if not Order.exists():
            return {'error': 'Commande introuvable.'}
        if Order.state != 'draft':
            return {'error': 'La commande doit être en état draft pour être modifiée.'}

        # 1) Supprimer toutes les lignes existantes
        request.env['pos.order.line'].sudo().search([('order_id', '=', Order.id)]).unlink()

        # 2) Créer les nouvelles lignes en renseignant TOUTES les colonnes obligatoires
        Product = request.env['product.product'].sudo()
        new_count = 0

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

            # Récupération des taxes du produit (ou fallback vide)
            taxes = prod.taxes_id.filtered(lambda t: t.company_id == Order.company_id)
            # Calcul du montant TTC

            price_subtotal_incl = price_subtotal
            for tax in taxes:
                # compute_excluded = False pour montant TTC

                tax_value = tax._compute_amount(price_subtotal, price_unit, qty, order=Order.id)
                price_subtotal_incl += tax_value

            # Nom de la ligne, reprend l'habitude POS
            line_name = "%s/%04d" % (Order.name, Order.sequence_number or 1)

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

        return {
            'success': True,
            'order_id': Order.id,
            'lines_count': new_count,
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
