import re

def process_css():
    with open('frontend/src/styles.css', 'r') as f:
        css = f.read()

    # First, handle specific classes that should only apply to live mode
    css = css.replace('.dev-ui-mode .layout {', '.mode-live .layout {')
    css = css.replace('.dev-ui-mode .play-column {', '.mode-live .play-column {')
    css = css.replace('.dev-ui-mode .story-grid {', '.mode-live .story-grid {')

    # Also handle the media query instances
    css = css.replace('  .dev-ui-mode .layout {', '  .mode-live .layout {')
    css = css.replace('  .dev-ui-mode .story-grid {', '  .mode-live .story-grid {')

    # Now replace ALL OTHER instances of .dev-ui-mode with a selector that targets both
    css = css.replace('.dev-ui-mode', '.mode-live, .mode-staging')

    # Remove the OLD .mode-live classes so we don't have duplicated conflicting logic
    # The old ones were `.mode-live .layout`, `.mode-live .side-column .status-panel`, etc.
    # To be very precise, let's just delete the exact strings of the old mode-live rules that conflict.
    
    old_rules = [
        ".mode-live .layout {\n  grid-template-columns: minmax(0, 1.72fr) minmax(300px, 0.72fr);\n}",
        ".mode-live .side-column .status-panel {\n  opacity: 0.86;\n}",
        ".mode-live .side-column .status-panel:hover {\n  opacity: 1;\n}",
        ".mode-live .story-grid {\n  grid-template-columns: minmax(0, 1.16fr) minmax(400px, 1fr);\n}"
    ]
    for old_rule in old_rules:
        css = css.replace(old_rule + '\n', '')
        css = css.replace(old_rule, '')

    with open('frontend/src/styles.css', 'w') as f:
        f.write(css)

if __name__ == '__main__':
    process_css()
