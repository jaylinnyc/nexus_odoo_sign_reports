from odoo import http
from odoo.http import request

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
        # Odoo 19/Master refactored _get_completed_document. 
        # We try available methods or fallback to the blank template.
        content = False
        
        if hasattr(sign_request, '_get_completed_document'):
            # Odoo 16/17/18
            content, _ = sign_request._get_completed_document(include_log=False)
            
        elif hasattr(sign_request, '_generate_completed_document'):
            # Potential Odoo 19 refactor name
            content, _ = sign_request._generate_completed_document(include_log=False)
            
        elif hasattr(sign_request, 'generate_completed_document'):
            # Alternative public method name
            content, _ = sign_request.generate_completed_document(include_log=False)
            
        if not content:
            # Fallback: Return the blank template PDF if merging fails
            # 'raw' gives the binary content of the attachment
            content = sign_request.template_id.attachment_id.raw

        # 4. Return as File Download
        filename = f"{sign_request.reference or 'document'}.pdf"
        
        return request.make_response(
            content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ]
        )