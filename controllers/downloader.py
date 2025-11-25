from odoo import http
from odoo.http import request
from werkzeug.exceptions import NotFound
import base64
import logging

_logger = logging.getLogger(__name__)

class SignControllerDynamic(http.Controller):
    
    @http.route('/sign/download/pdf_only/<int:request_id>/<string:token>', type='http', auth='public')
    def download_pdf_only(self, request_id, token, **kwargs):
        """
        Custom endpoint to download ONLY the PDF.
        Attempts to generate the completed doc first, falls back to the blank template.
        """
        # 1. Load Request
        sign_request = request.env['sign.request'].sudo().browse(request_id)
        
        # 2. Security Check
        if not sign_request.exists() or sign_request.access_token != token:
            _logger.warning(f"Sign Download: Security Fail. ReqID: {request_id}, Token: {token}")
            raise NotFound()

        _logger.info(f"Sign Download: Starting download for Request {request_id}")

        content = False
        filename = f"{sign_request.reference or 'document'}.pdf"

        # ---------------------------------------------------------
        # Attempt A: Try to get the "Completed" doc (Values Filled)
        # ---------------------------------------------------------
        # Note: Odoo 19/Master is refactoring this. We try known method names.
        methods = ['_get_completed_document', 'generate_completed_document', '_generate_completed_document']
        for method in methods:
            if hasattr(sign_request, method):
                try:
                    _logger.info(f"Sign Download: Trying method {method}")
                    # Try to get content. Some methods return (data, filetype), others just data.
                    result = getattr(sign_request, method)(include_log=False)
                    
                    if isinstance(result, tuple):
                        content = result[0]
                    else:
                        content = result
                        
                    if content:
                        _logger.info("Sign Download: Success via method generation.")
                        break
                except Exception as e:
                    _logger.error(f"Sign Download: Method {method} failed: {e}")
                    continue

        # ---------------------------------------------------------
        # Attempt B: Fallback to BLANK Template (No Values Filled)
        # ---------------------------------------------------------
        if not content:
            _logger.warning("Sign Download: Could not generate completed doc. Falling back to template.")
            template = sign_request.template_id
            
            # 1. Check 'attachment_ids' (Newer Odoo)
            if hasattr(template, 'attachment_ids') and template.attachment_ids:
                content = template.attachment_ids[0].raw
                _logger.info("Sign Download: Found via template.attachment_ids")

            # 2. Check 'attachment_id' (Older Odoo)
            elif hasattr(template, 'attachment_id') and template.attachment_id:
                content = template.attachment_id.raw
                _logger.info("Sign Download: Found via template.attachment_id")

            # 3. Last Resort: Search ir.attachment table directly
            # Sometimes fields are removed but the attachment link exists in the DB
            if not content:
                attachments = request.env['ir.attachment'].sudo().search([
                    ('res_model', '=', 'sign.template'),
                    ('res_id', '=', template.id),
                    ('mimetype', '=', 'application/pdf')
                ], limit=1)
                if attachments:
                    content = attachments.raw
                    _logger.info("Sign Download: Found via direct ir.attachment search")

        # ---------------------------------------------------------
        # Final Output
        # ---------------------------------------------------------
        if not content:
            _logger.error(f"Sign Download: FATAL - No content found for Request {request_id} / Template {sign_request.template_id.id}")
            raise NotFound()

        return request.make_response(
            content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ]
        )