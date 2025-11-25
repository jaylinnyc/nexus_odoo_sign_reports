from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'

    def action_preview(self):
        """ 
        Opens the document in a new tab (Viewer Mode).
        """
        request = self.create_request()
        # No extra population call needed here as create_request handles it
        return {
            'type': 'ir.actions.act_url',
            'url': f'/sign/document/{request.id}/{request.access_token}',
            'target': 'new',
        }

    def action_download_preview(self):
        """ 
        Standard Download:
        Creates the request and triggers the standard Odoo download endpoint.
        """
        request = self.create_request()
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/sign/download/{request.id}/{request.access_token}/completed',
            'target': 'self',
        }

    def create_request(self):
        """ Override standard creation to populate fields from context. """
        request = super(SignSendRequest, self).create_request()
        
        # Defensive: Ensure request is a browse record, not just an ID
        if isinstance(request, int):
            request = self.env['sign.request'].browse(request)
            
        self._populate_fields_from_context(request)
        return request

    def _get_eval_context(self, source_record):
        """
        Builds a dictionary of objects available to the Sign Template.
        This allows items to reference 'product.name', 'salesorder.amount_total', etc.
        """
        context = {
            'record': source_record,   # Default reference
            'user': self.env.user,
            'company': self.env.company,
        }

        # Add model-specific aliases
        if source_record._name == 'sale.order':
            context['salesorder'] = source_record
            context['order'] = source_record
            context['partner'] = source_record.partner_id
            # Add the first product found (as requested)
            if source_record.order_line:
                context['product'] = source_record.order_line[0].product_id
                
        elif source_record._name == 'purchase.order':
            context['purchaseorder'] = source_record
            context['order'] = source_record
            context['partner'] = source_record.partner_id
            if source_record.order_line:
                context['product'] = source_record.order_line[0].product_id

        return context

    def _populate_fields_from_context(self, request):
        """ 
        Resolves Sign Item names against the context objects.
        Supported formats:
        - 'object_key.field_name' (e.g., 'product.name', 'salesorder.amount_total')
        - 'field_name' (Implicitly checks the main record)
        """
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')

        if not request or not active_model or not active_id:
            return

        if active_model not in ['sale.order', 'purchase.order']:
            return

        source_record = self.env[active_model].browse(active_id)
        eval_context = self._get_eval_context(source_record)
        values_to_write = []
        
        _logger.info(f"Sign Context: Processing with context keys: {list(eval_context.keys())}")

        for item in request.template_id.sign_item_ids:
            if not item.name:
                continue

            value = None
            
            # Logic: Is it a path (e.g. "product.name") or a direct field?
            if '.' in item.name:
                # Path traversal: "product.name" -> obj="product", field="name"
                parts = item.name.split('.')
                obj_key = parts[0]
                field_path = parts[1:]
                
                if obj_key in eval_context:
                    current_obj = eval_context[obj_key]
                    try:
                        # Traverse fields (e.g. product.categ_id.name)
                        for field_name in field_path:
                            current_obj = getattr(current_obj, field_name)
                        value = current_obj
                    except AttributeError:
                        _logger.warning(f"Sign Context: Could not traverse '{item.name}'")
            else:
                # Direct field on main record fallback (Legacy support)
                if hasattr(source_record, item.name):
                    value = getattr(source_record, item.name)

            # Convert result to string for Sign
            if value is not None:
                str_value = ''
                if isinstance(value, models.Model):
                    str_value = value.display_name
                elif isinstance(value, (float, int)):
                    str_value = str(value)
                elif value:
                    str_value = str(value)
                
                if str_value:
                    values_to_write.append({
                        'sign_request_id': request.id,
                        'sign_item_id': item.id,
                        'value': str_value,
                    })
                    _logger.info(f"Sign Context: Set '{item.name}' -> '{str_value}'")

        if values_to_write:
            self.env['sign.request.item.value'].create(values_to_write)