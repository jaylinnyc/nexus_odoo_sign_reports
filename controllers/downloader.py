from odoo import http
from odoo.http import request
import base64

class SignControllerDynamic(http.Controller):
    
    @http.route('/sign/download/pdf_only/<int:request_id>/<string:token>', type='http', auth='public')
    def download_pdf_only(self, request_id, token, **kwargs):
        """
        Custom endpoint to download ONLY the PDF (with values filled),
        skipping the Certificate/Audit Log ZIP generation.
        """
        # 1. Load Request
        sign_request = request.env['sign.request'].sudo().browse(request_id)
        
        # 2. Security Check
        if not sign_request.exists() or sign_request.access_token != token:
            return request.not_found()

        # 3. Generate PDF
        content = False
        
        # Attempt A: Get Signed/Completed Document via Methods
        # Odoo 16/17/18/19 vary in method names
        methods_to_try = ['_get_completed_document', 'generate_completed_document', '_generate_completed_document']
        
        for method_name in methods_to_try:
            if hasattr(sign_request, method_name):
                try:
                    # include_log=False is key to getting just the PDF
                    result = getattr(sign_request, method_name)(include_log=False)
                    # Result is usually (content, mimetype)
                    if isinstance(result, tuple):
                        content = result[0]
                    else:
                        content = result
                    if content:
                        break
                except Exception:
                    continue

        # Attempt B: Check for direct stored binary fields (if method generation fails)
        if not content:
            if hasattr(sign_request, 'completed_document') and sign_request.completed_document:
                content = base64.b64decode(sign_request.completed_document)

        # Attempt C: Fallback to Original Template PDF (Blank/Unsigned)
        # Handle Odoo 19 "Multi-Document" refactor where attachment_id might be attachment_ids
        if not content:
            template = sign_request.template_id
            
            # Case 1: Standard/Legacy Single Attachment
            if hasattr(template, 'attachment_id') and template.attachment_id:
                content = template.attachment_id.raw
            
            # Case 2: Odoo 19 Multi-Document (Take the first one)
            elif hasattr(template, 'attachment_ids') and template.attachment_ids:
                content = template.attachment_ids[0].raw
                
            # Case 3: Documents App Integration
            elif hasattr(template, 'document_id') and template.document_id:
                content = template.document_id.raw

        # 4. Return as File Download
        if not content:
            return request.not_found()

        filename = f"{sign_request.reference or 'document'}.pdf"
        
        return request.make_response(
            content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ]
        )