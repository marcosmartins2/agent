import subprocess
import sys

# Get the original file from git
result = subprocess.run(
    ['git', 'show', 'HEAD:templates/agents/form_new.html'],
    capture_output=True,
    cwd=r'c:\Users\ruben\OneDrive\Documentos\GitHub\agent'
)

if result.returncode != 0:
    print(f'Git error: {result.stderr.decode("utf-8", errors="replace")}')
    sys.exit(1)

# Decode as utf-8 (git outputs utf-8)
content = result.stdout.decode('utf-8')

# Fix 1: Lines 157-160 (first multi-line if tag)
old1 = '''                    <input type="radio" name="status_toggle_display" id="status_{{ value }}_top" value="{{ value }}"
                        onchange="document.getElementById('status_toggle_hidden').value = this.value" {% if
                        form.status_toggle.value==value or value=='ativo' and not form.status_toggle.value %}checked{%
                        endif %}>'''

new1 = '''                    <input type="radio" name="status_toggle_display" id="status_{{ value }}_top" value="{{ value }}" onchange="document.getElementById('status_toggle_hidden').value = this.value" {% if form.status_toggle.value == value or value == 'ativo' and not form.status_toggle.value %}checked{% endif %}>'''

# Fix 2: Lines 260-262 (second multi-line if tag)
old2 = '''                        <input type="radio" name="status_toggle" id="status_{{ value }}" value="{{ value }}" {% if
                            form.status_toggle.value==value or value=='ativo' and not form.status_toggle.value
                            %}checked{% endif %}>'''

new2 = '''                        <input type="radio" name="status_toggle" id="status_{{ value }}" value="{{ value }}" {% if form.status_toggle.value == value or value == 'ativo' and not form.status_toggle.value %}checked{% endif %}>'''

# Apply fixes
if old1 in content:
    content = content.replace(old1, new1)
    print('Fix 1 applied (lines 157-160)')
else:
    print('Fix 1 target not found')

if old2 in content:
    content = content.replace(old2, new2)
    print('Fix 2 applied (lines 260-262)')
else:
    print('Fix 2 target not found')

# Write to the file
target = r'c:\Users\ruben\OneDrive\Documentos\GitHub\agent\templates\agents\form_new.html'
with open(target, 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(content)

print(f'Successfully wrote {len(content)} bytes to {target}')

# Verify
with open(target, 'r', encoding='utf-8') as f:
    verify = f.read()

if new2 in verify:
    print('VERIFIED: Fix is present in written file!')
else:
    print('ERROR: Fix NOT in written file!')
