# from odoo import http


# class NexusOdooSignReports(http.Controller):
#     @http.route('/nexus_odoo_sign_reports/nexus_odoo_sign_reports', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nexus_odoo_sign_reports/nexus_odoo_sign_reports/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('nexus_odoo_sign_reports.listing', {
#             'root': '/nexus_odoo_sign_reports/nexus_odoo_sign_reports',
#             'objects': http.request.env['nexus_odoo_sign_reports.nexus_odoo_sign_reports'].search([]),
#         })

#     @http.route('/nexus_odoo_sign_reports/nexus_odoo_sign_reports/objects/<model("nexus_odoo_sign_reports.nexus_odoo_sign_reports"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nexus_odoo_sign_reports.object', {
#             'object': obj
#         })

