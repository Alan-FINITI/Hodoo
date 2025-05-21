from odoo import api, fields, models


class RefugeManagement(models.Model):
    _name = "refuge.management"
    _description = "Refuge Management"
    import logging
    _logger = logging.getLogger(__name__)
    @api.model
    def load_refuge_data(self):

        """
        Charge les données principales pour l'application
        """
        products = self.env["product.template"].search_read(
            fields=[
                'name',
                'list_price',
                'description',
                'description_sale',  # Description commerciale
                'image_1920',
                'id',
                'categ_id',
                'bom_ids',  # IDs des nomenclatures associées
                'available_in_pos',
                'qty_available',
            ]
        )

        # Récupérer les nomenclatures pour les produits
        bom_data = {}
        bom_ids = [bom_id for product in products for bom_id in product.get('bom_ids', [])]

        if bom_ids:
            boms = self.env["mrp.bom"].search_read(
                [('id', 'in', bom_ids)],
                fields=['product_tmpl_id', 'bom_line_ids']
            )

            # Récupérer les lignes de nomenclature
            bom_line_ids = [line_id for bom in boms for line_id in bom.get('bom_line_ids', [])]
            if bom_line_ids:
                bom_lines = self.env["mrp.bom.line"].search_read(
                    [('id', 'in', bom_line_ids)],
                    fields=['bom_id', 'product_id', 'product_qty', 'product_uom_id']
                )

                # Organiser les lignes par BOM
                line_by_bom = {}
                for line in bom_lines:
                    if line['bom_id'][0] not in line_by_bom:
                        line_by_bom[line['bom_id'][0]] = []

                    # Obtenir le nom du produit pour cette ligne
                    product_info = self.env["product.product"].browse(line['product_id'][0]).read(['name', 'uom_id'])
                    uom_name = self.env["uom.uom"].browse(line['product_uom_id'][0]).name

                    line_by_bom[line['bom_id'][0]].append({
                        'product_name': product_info[0]['name'],
                        'quantity': line['product_qty'],
                        'uom': uom_name
                    })

                # Lier les boms aux produits
                for bom in boms:
                    product_tmpl_id = bom['product_tmpl_id'][0]
                    bom_data[product_tmpl_id] = {
                        'bom_id': bom['id'],
                        'ingredients': line_by_bom.get(bom['id'], [])
                    }

        available_products = []
        for product in products:
            if product['available_in_pos'] and product['qty_available']:
                self._logger.info(product)
                # Ajouter l'URL de l'image
                if product.get('image_1920'):
                    product[
                        'image_url'] = f"http://localhost:8070/web/image?model=product.template&id={product['id']}&field=image_1920"
                else:
                    product['image_url'] = None

                # Ajouter les données de nomenclature
                product_id = product['id']
                if product_id in bom_data:
                    product['ingredients'] = bom_data[product_id]['ingredients']
                else:
                    product['ingredients'] = []

                available_products.append(product)

        return {
            "product.template": available_products,
        }
