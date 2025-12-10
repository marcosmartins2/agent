import re

# Read file
with open('templates/agents/form_new.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all multi-line template tags - pattern for {% if ... on one line and rest on next
# Replace all occurrences of {% if followed by newline+content+%}checked{% endif %}
pattern = r'\{% if\s*\n\s*form\.status_toggle\.value==value or value==.ativo. and not form\.status_toggle\.value\s*\n\s*%\}checked\{% endif %\}'
replacement = '{% if form.status_toggle.value == value or value == "ativo" and not form.status_toggle.value %}checked{% endif %}'

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Also handle the variant with {% if at end of line
pattern2 = r'\{% if\s+\n\s*form\.status_toggle\.value==value or value==.ativo. and not form\.status_toggle\.value\s*%\}checked\{%\s*\n\s*endif %\}'
content = re.sub(pattern2, replacement, content, flags=re.DOTALL)

# Direct string replacement for the exact problematic pattern
old_str = '''{% if
                            form.status_toggle.value==value or value=='ativo' and not form.status_toggle.value
                            %}checked{% endif %}'''
new_str = '{% if form.status_toggle.value == value or value == "ativo" and not form.status_toggle.value %}checked{% endif %}'
content = content.replace(old_str, new_str)

# Also handle similar pattern with different indentation
old_str2 = '''{% if
                        form.status_toggle.value==value or value=='ativo' and not form.status_toggle.value %}checked{%
                        endif %}'''
content = content.replace(old_str2, new_str)

# Write back
with open('templates/agents/form_new.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed template tags')
