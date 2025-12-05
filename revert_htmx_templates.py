import os
import glob

# We need to remove the conditional extends approach
# Instead, we'll handle this in the views by detecting HTMX requests

template_dir = 'templates/store'
templates = glob.glob(f'{template_dir}/*.html')

for filepath in templates:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the HTMX conditional wrapper
    if '{% if not request.META.HTTP_HX_REQUEST %}' in content:
        # Remove the conditional lines
        content = content.replace('{% if not request.META.HTTP_HX_REQUEST %}\n  {% extends \'layouts/app.html\' %}\n{% endif %}\n', '{% extends \'layouts/app.html\' %}\n')
        
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        print(f'Fixed {os.path.basename(filepath)}')

print('\nAll templates reverted to standard extends!')
print('Will handle HTMX in views instead.')
