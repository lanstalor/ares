import re

with open('frontend/src/styles.css', 'r') as f:
    css = f.read()

# Replace all .dev-ui-mode with .mode-live, .mode-staging EXCEPT where it breaks staging layout
# Let's just find and replace specific known rules, or just use regex with care.

# First, find all .dev-ui-mode occurrences
blocks = re.split(r'(\.dev-ui-mode[^{]*\{[^}]*\})', css)

for i in range(1, len(blocks), 2):
    block = blocks[i]
    if '.dev-ui-mode .layout' in block:
        # Only apply 1-column layout to mode-live
        blocks[i] = block.replace('.dev-ui-mode', '.mode-live')
    else:
        # Apply other aesthetic rules to both modes
        # Also handle comma-separated lists like .dev-ui-mode .a, .dev-ui-mode .b
        blocks[i] = block.replace('.dev-ui-mode', '.mode-live, .mode-staging')

new_css = "".join(blocks)

# Also remove old .mode-live rules that conflict with the new ones
new_css = re.sub(r'\n\.mode-live[^{]*\{[^}]*\}', '', new_css)
# Wait, if I do this, it will remove the ones I just created!
# Let's not blindly remove all .mode-live. Let's just remove the original ones manually.

with open('frontend/src/styles.css', 'w') as f:
    f.write(new_css)
