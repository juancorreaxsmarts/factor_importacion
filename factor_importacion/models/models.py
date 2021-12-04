# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
READONLY_STATES = {
        'draft': [('readonly', False)],
        'completed': [('readonly', True)]}

EXPENSES = [('expense1', 'Transporte / Flete'),
            ('expense2', 'Tasa Servicio Aduanero'),
            ('expense3', 'Declaracion Unica Aduanera'),
            ('expense4', 'Impuestos Arancelarios'),
            ('expense5', 'Impuesto Selectivo'),
            ('expense6', 'Impuesto Transferencia de Bienes'),
            ('expense7', 'Valores'),
            ('expense8', 'Transporte Terrestre'),
            ('expense9', 'Haina Internacional Terminals'),
            ('expense10','Portuaria'),
            ('expense11','DPWorld Transporte'),
            ('expense12','Gestion Aduanal')]

class acint_purchase(models.Model):
    _name = 'acint_purchase.acint_purchase'
    _description = 'acint_purchase.acint_purchase'

    state = fields.Selection(string=u'Estado', default='draft', selection=[('draft', 'Borrador'), ('completed', 'Compleado')])
    name = fields.Char(string=u'Referencia', readonly=True)
    purchase_orders = fields.Many2many(string=u'Ordenes de Compra', comodel_name='purchase.order', relation='order_import_factor_rel', column1='import_factor_id', column2='order_id', states=READONLY_STATES)
    purchase_orders_total_usd =  fields.Float(string='Total Compras USD', states=READONLY_STATES)
    purchase_orders_total_dop =  fields.Float(string='Total Compras DOP', states=READONLY_STATES)
    handling_transfer_amount = fields.Float(string='Traspaso y Manejo', states=READONLY_STATES)
    expenses_purchase = fields.One2many('acint.purchase.import.expenses.v', 'import_factor_id', string=u'Otros Gastos (DOP)', states=READONLY_STATES)
    factor_import_amount = fields.Float(string='Factor General de Importacion', states=READONLY_STATES)
    usd_rate = fields.Float(string=u'Tasa Dolar', states=READONLY_STATES)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('import.factor.number')
        return super(acint_purchase, self).create(vals)

    @api.onchange('purchase_orders','usd_rate')
    def _getTotalPurchase(self):
        total_dop = 0
        total_usd = 0

        for po in self.purchase_orders:

            if self.usd_rate > 0:

                for ol in po.order_line:

                    if ol.product_id.type != "service":

                        if po.currency_id.name == "DOP":
                            total_dop += ol.price_subtotal
                            total_usd += ol.price_subtotal / self.usd_rate
                        else:
                            total_dop += ol.price_subtotal * self.usd_rate
                            total_usd += ol.price_subtotal

        self.purchase_orders_total_usd = total_usd
        self.purchase_orders_total_dop = total_dop

    @api.onchange('expenses_purchase', 'handling_transfer_amount', 'purchase_orders','usd_rate')
    def _getTotalImportFactor(self):
        total = 0

        for e in self.expenses_purchase:
            if e.expenses_amount > 0:
                total += e.expenses_amount

        if self.usd_rate > 0 and self.purchase_orders_total_dop > 0:
            self.factor_import_amount = (total + self.purchase_orders_total_dop + self.handling_transfer_amount) / self.purchase_orders_total_usd


    def complete(self):

        for po in self.purchase_orders:

            for ol in po.order_line:

                if ol.product_id.type != "service":

                    if po.currency_id.name == "DOP":
                        new_price_unit = (ol.price_unit / self.usd_rate) * self.factor_import_amount
                    else:
                        new_price_unit = ol.price_unit * self.factor_import_amount

                    ol.unit_price_dop = new_price_unit

            po.import_factor_id = self.id
        self.state = "completed"


    def draft(self):
        self.state = "draft"



class ImportExpenses(models.Model):
    _name = 'acint.purchase.import.expenses.v'
    _description = 'Modulo para registrar los gastos de importacion'

    expenses_list = fields.Selection(string=u'Gasto', selection=EXPENSES)
    expenses_amount = fields.Float(string=u'Monto')
    import_factor_id = fields.Many2one('acint_purchase.acint_purchase', string='Factor de Importacion')

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    import_factor_id = fields.Many2one('acint_purchase.acint_purchase', string='Factor de Importacion')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    unit_price_dop = fields.Float(string="Precio FI (DOP)")

class PurchaseOrderProduct(models.Model):
    _inherit = 'product.template'

    coste_real = fields.Float(string=u"Coste Real")
    coste_real_fake = fields.Float(string=u"Coste Real")
