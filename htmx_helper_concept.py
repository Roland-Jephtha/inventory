# HTMX Helper for Views
# Add this to store/views.py or create a utils.py file

def render_with_htmx(request, template_name, context=None):
    """
    Helper function to render templates with HTMX support.
    Returns partial content for HTMX requests, full page otherwise.
    """
    if context is None:
        context = {}
    
    # Check if this is an HTMX request
    is_htmx = request.META.get('HTTP_HX_REQUEST') == 'true'
    
    if is_htmx:
        # For HTMX, create a minimal template that only renders the content block
        # We'll use a wrapper template
        context['htmx_template'] = template_name
        return render(request, 'htmx_wrapper.html', context)
    else:
        # Normal request, render full page
        return render(request, template_name, context)
