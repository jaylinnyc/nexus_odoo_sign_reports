# from odoo import models, fields, api


# class nexus_odoo_sign_reports(models.Model):
#     _name = 'nexus_odoo_sign_reports.nexus_odoo_sign_reports'
#     _description = 'nexus_odoo_sign_reports.nexus_odoo_sign_reports'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

