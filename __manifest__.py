{
    'name': 'Sign Integration: Dynamic Sales & Purchase',
    'version': '1.0',
    'category': 'Document Management',
    'summary': 'Auto-fill Sign templates from SO/PO and add Preview option',
    'description': """
        This module extends the standard 'Request Signature' wizard in Odoo.
        
        Features:
        1. Auto-population: When requesting a signature from a Sale or Purchase Order, 
           if the Sign Template has text fields matching field names on the order 
           (e.g., 'amount_total', 'partner_id'), they are automatically filled.
        2. Preview Button: Adds a 'Preview' button to the wizard, allowing you 
           to verify the populated document in a new tab before sending.
    """,
    'depends': ['sign', 'sale', 'purchase'],
    'data': [
        'views/sign_send_request_views.xml',
    ],
    'installable': True,
    'license': 'OEEL-1',
}