from odoo import api, models, fields


class ClientWeb(models.Model):
    _name = "refuge.clientWeb"
    _description = "Client Web"
    _inherit_ = "res.partner"

    fidelity_points = fields.Integer(string="Points de fidélité")

    discount = fields.Float(string = "Reduction totale", compute="calculate_discount", default=1)

    @api.model
    def calculate_discount(self):
        if self.fidelity_points >= 1000:
            self.discount = 0.8
        elif self.fidelity_points >= 500:
            self.discount = 0.85
        elif self.fidelity_points >= 200:
            self.discount = 0.90
        elif self.fidelity_points >= 100:
            self.discount = 0.95

