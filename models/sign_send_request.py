from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'

    def action_preview(self):
        """ 
        Opens the document in a new tab (Viewer Mode).
        Uses standard Odoo create_request logic.
        """
        request = self.create_request()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/sign/document/{request.id}/{request.access_token}',
            'target': 'new',
        }

    def action_download_preview(self):
        """ 
        Standard Download:
        Creates the request using standard logic and triggers the standard Odoo download endpoint.
        """
        request = self.create_request()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/sign/download/{request.id}/{request.access_token}/completed',
            'target': 'self',
        }

    # Removed: create_request override
    # Removed: _populate_fields_from_context
    # Removed: _get_eval_context
    # This ensures we are testing 100% standard Odoo behavior + our buttons.