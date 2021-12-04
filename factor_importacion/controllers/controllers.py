# -*- coding: utf-8 -*-
# from odoo import http


# class AcintPurchase(http.Controller):
#     @http.route('/acint_purchase/acint_purchase/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/acint_purchase/acint_purchase/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('acint_purchase.listing', {
#             'root': '/acint_purchase/acint_purchase',
#             'objects': http.request.env['acint_purchase.acint_purchase'].search([]),
#         })

#     @http.route('/acint_purchase/acint_purchase/objects/<model("acint_purchase.acint_purchase"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('acint_purchase.object', {
#             'object': obj
#         })
