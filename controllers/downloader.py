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
        # get_completed_document() returns (pdf_bytes, 'application/pdf') for the filled/signed PDF only
        content, content_type = sign_request.get_completed_document()
        
        # 4. Return as File Download
        filename = f"{sign_request.reference or 'document'}.pdf"
        
        return request.make_response(
            content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ]
        )