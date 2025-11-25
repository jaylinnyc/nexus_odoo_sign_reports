from odoo import models, fields, api, _

class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'

    def action_preview(self):
        """ 
        Opens the document in a new tab (Viewer Mode).
        """
        request = self.create_request()
        self._populate_dynamic_fields(request)
        return {
            'type': 'ir.actions.act_url',
            'url': f'/sign/document/{request.id}/{request.access_token}',
            'target': 'new',
        }

    def action_download_preview(self):
        """ 
        Standard Download:
        Creates the request, populates data, and triggers the standard Odoo 
        download endpoint. This returns a ZIP file containing the PDF and Audit Log.
        """
        request = self.create_request()
        self._populate_dynamic_fields(request)

        # Standard Odoo Endpoint
        return {
            'type': 'ir.actions.act_url',
            'url': f'/sign/download/{request.id}/{request.access_token}/completed',
            'target': 'self',
        }

    def create_request(self):
        """ Override standard creation to ensure dynamic fields are always populated. """
        request = super(SignSendRequest, self).create_request()
        self._populate_dynamic_fields(request)
        return request

    def _populate_dynamic_fields(self, request):
        """ Introspects the context and fills matching fields. """
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')

        if not request or not active_model or not active_id:
            return

        if active_model not in ['sale.order', 'purchase.order']:
            return

        source_record = self.env[active_model].browse(active_id)
        values_to_write = []
        
        for item in request.template_id.sign_item_ids:
            if not item.name:
                continue

            if hasattr(source_record, item.name):
                field_value = getattr(source_record, item.name)
                
                str_value = ''
                if isinstance(field_value, models.Model):
                    str_value = field_value.display_name
                elif isinstance(field_value, (float, int)):
                    str_value = str(field_value)
                elif field_value:
                    str_value = str(field_value)
                
                if str_value:
                    values_to_write.append({
                        'sign_request_id': request.id,
                        'sign_item_id': item.id,
                        'value': str_value,
                    })

        if values_to_write:
            self.env['sign.request.item.value'].create(values_to_write)