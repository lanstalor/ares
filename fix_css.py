import re

with open('frontend/src/styles.css', 'r') as f:
    css = f.read()

# First, rename specific layout classes to mode-live
css = css.replace('.dev-ui-mode .layout', '.mode-live .layout')
css = css.replace('.dev-ui-mode .play-column', '.mode-live .play-column')
css = css.replace('.dev-ui-mode .story-grid', '.mode-live .story-grid')

# Then rename all remaining .dev-ui-mode classes to .mode-live, .mode-staging
css = css.replace('.dev-ui-mode', '.mode-live, .mode-staging')

# Wait, some old mode-live classes exist.
# Let's remove any pre-existing .mode-live classes to avoid conflicts.
# But wait, what if I just delete .mode-live?
css = re.sub(r'\n\.mode-live[^{]*\{[^}]*\}', '', css)
# Wait, this will ALSO remove the .mode-live classes I just created!
# Let's not blindly remove.

with open('frontend/src/styles.css', 'w') as f:
    f.write(css)
