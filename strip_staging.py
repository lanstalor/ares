import re

def main():
    with open('frontend/src/styles.css', 'r') as f:
        css = f.read()

    # We need to find rules where the selector contains '.mode-staging'.
    # A rule looks like: selector, selector { \n body \n }
    # We will use regex to find all top-level blocks.
    # This regex matches a block: optionally preceded by whitespace, followed by selectors, then { body }
    
    # Simple regex to remove any block that has .mode-staging as the ONLY selector, or as part of a list.
    # It's safer to just remove any block containing .mode-staging, IF it only contains .mode-staging selectors.
    # Let's see all occurrences from grep earlier. They are all single-selector or multi-selector where ALL selectors are .mode-staging.
    
    # Find all blocks: `selectors { body }`
    # We'll replace blocks that match `.mode-staging[^{]*\{[^}]*\}`
    # To handle commas, let's just use a loop over regex matches.
    
    # We will remove blocks where the entire selector string contains .mode-staging
    # Example:
    # .mode-staging .layout {
    #   ...
    # }
    
    # regex: `(?:^|\n|\})\s*(\.mode-staging[^{]*\{[^}]*\})`
    # It's better to just do `\n\.mode-staging[^{]*\{[^}]*\}`
    
    new_css = re.sub(r'\n\.mode-staging[^{]*\{[^}]*\}', '', css)
    
    with open('frontend/src/styles.css', 'w') as f:
        f.write(new_css)

if __name__ == '__main__':
    main()
