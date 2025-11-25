from odoo import models, fields, api, _

class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'

    def action_preview(self):
        """ Creates the request, populates data, and opens the preview URL (no email sent). """
        # 1. Create the request using Odoo's standard method
        request = self.create_request()
        
        # 2. Inject our custom logic to fill fields from SO/PO
        self._populate_dynamic_fields(request)

        # 3. Open the signing interface in a new tab
        return {
            'type': 'ir.actions.act_url',
            'url': f'/sign/document/{request.id}/{request.access_token}',
            'target': 'new',
        }

    def send_request(self):
        """ Override standard send to ensure fields are populated before emailing. """
        # We wrap the original method to ensure data is filled if they click 'Send' directly
        # Note: We can't easily hook *inside* send_request without replacing it, 
        # so we create the request first if possible, or we rely on the fact 
        # that send_request calls create_request internally.
        
        # Ideally, we hook into create_request, but create_request returns an ID, not an object in some versions.
        # Safer approach: Let standard logic run, but if we need population, we do it.
        
        # However, standard send_request creates AND sends. 
        # We will iterate the created requests after `super`.
        
        res = super(SignSendRequest, self).send_request()
        
        # Find the request created by this wizard context
        # This is tricky because super returns an action. 
        # A safer bet is to populate logic triggered by the Action button context.
        return res

    def create_request(self):
        """ Override the creation to inject data population immediately. """
        request = super(SignSendRequest, self).create_request()
        self._populate_dynamic_fields(request)
        return request

    def _populate_dynamic_fields(self, request):
        """
        Pull data from the active_model (Sale/Purchase) and fill Sign Items.
        """
        # 1. Check Context for Source Record
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')

        if not active_model or not active_id or not request:
            return

        # Only run for supported models to avoid errors
        if active_model not in ['sale.order', 'purchase.order']:
            return

        source_record = self.env[active_model].browse(active_id)
        
        values_to_write = []
        
        # 2. Iterate template items linked to this request
        # Note: request.template_id.sign_item_ids gives the definitions
        # We need to map them to the actual 'sign.request.item.value'
        
        for item in request.template_id.sign_item_ids:
            if not item.name:
                continue

            # 3. Match Field Names
            # If Sign Template Item name matches an Odoo field name (e.g. 'amount_total')
            if hasattr(source_record, item.name):
                field_value = getattr(source_record, item.name)
                
                # Convert value to string
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

        # 4. Bulk Create Values
        if values_to_write:
            self.env['sign.request.item.value'].create(values_to_write)