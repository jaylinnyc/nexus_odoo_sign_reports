{
    'name': 'Sign Integration: Dynamic Sales & Purchase',
    'version': '1.1',
    'category': 'Document Management',
    'summary': 'Auto-fill Sign templates and Preview/Download as PDF',
    'description': """
        This module extends the standard 'Request Signature' wizard in Odoo.
        
        Features:
        1. Auto-population: When requesting a signature from a Sale or Purchase Order, 
           if the Sign Template has text fields matching field names on the order 
           (e.g., 'amount_total', 'partner_id'), they are automatically filled.
        2. Preview: View the filled document in a new tab.
        3. Download PDF: Download the filled document as a PDF (not ZIP).
    """,
    'depends': ['sign', 'sale', 'purchase'],
    'data': [
        'views/sign_send_request_views.xml',
    ],
    'installable': True,
    'license': 'OEEL-1',
}