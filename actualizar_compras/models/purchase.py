# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, api, exceptions, fields
from openerp.exceptions import Warning, ValidationError

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    def update_product_cost_price(self):

        for po in self.order_line:

            if po.update_cost_price:

                prod_obj = self.env['product.template'].search([('name', '=', po.product_id.name)])

                if po.unit_price_dop > 0:
                    cost_price = po.unit_price_dop
                    list_price = po.unit_price_dop * (1 + (prod_obj.percent_price/100))
                else:
                    cost_price = po.unit_price
                    list_price = po.unit_price * (1 + (prod_obj.percent_price/100))

                lst_price  = list_price

                #prod_value = {'list_price': list_price, 'lst_price':lst_price, 'standard_price': cost_price}
                prod_value = {'standard_price': cost_price}
                obj = prod_obj.write(prod_value)

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    update_cost_price = fields.Boolean(string="Actualizar costo?", default= True, help="Select to update cost price of product after confirming invoice")
