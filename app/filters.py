from markupsafe import Markup

def nl2br(value):
    """Convert newlines in text to HTML line breaks."""
    if not value:
        return ''
    return Markup(value.replace('\n', '<br>'))
