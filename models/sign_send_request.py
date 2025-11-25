from odoo import models, fields, api, _

class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'

    def action_preview(self):
        """ 
        Opens the document in a new tab (Viewer Mode).
        This allows the user to see the filled values before deciding to send.
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
        Creates the request, populates data, and immediately triggers 
        a download of the PDF using our custom controller.
        
        This points to '/sign/download/pdf_only/...' to avoid Odoo
        zipping the file with the audit log.
        """
        request = self.create_request()
        self._populate_dynamic_fields(request)

        return {
            'type': 'ir.actions.act_url',
            'url': f'/sign/download/pdf_only/{request.id}/{request.access_token}',
            'target': 'self', # 'self' triggers the browser download dialog
        }

    def create_request(self):
        """ 
        Override standard creation to ensure dynamic fields are always populated,
        whether the user clicks 'Send' or 'Sign Now' or 'Preview'.
        """
        request = super(SignSendRequest, self).create_request()
        self._populate_dynamic_fields(request)
        return request

    def _populate_dynamic_fields(self, request):
        """ 
        Introspects the context to find the source record (SO/PO) and 
        fills matching fields in the Sign Request.
        """
        # 1. Check Context for Source Record
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')

        # Guard clauses
        if not request or not active_model or not active_id:
            return

        if active_model not in ['sale.order', 'purchase.order']:
            return

        source_record = self.env[active_model].browse(active_id)
        
        values_to_write = []
        
        # 2. Iterate template items linked to this request
        for item in request.template_id.sign_item_ids:
            # Skip items without names
            if not item.name:
                continue

            # 3. Match Field Names
            # If the Sign Item name (e.g., 'amount_total') exists on the source record
            if hasattr(source_record, item.name):
                field_value = getattr(source_record, item.name)
                
                # Convert value to string (Sign requires text values)
                str_value = ''
                if isinstance(field_value, models.Model):
                    # Handle Many2one fields (e.g., partner_id -> "Gemini Inc.")
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

        # 4. Bulk Create Values
        if values_to_write:
            self.env['sign.request.item.value'].create(values_to_write)