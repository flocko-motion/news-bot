from datetime import datetime
from pathlib import Path
import chevron


def format_digest(digest: str) -> str:
	"""Format the digest by adding HTML page structure and the current date."""
	current_date = datetime.now().strftime("%d.%m.%Y")

	return f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <title>Neues aus der Region - {current_date}</title>
        </head>
        <body>
            <h1>Neues aus der Region - {current_date}</h1>
            {digest}
        </body>
        </html>
    """


def generate_digest_index(digests_dir: Path) -> str:
	"""Generate an index.html file listing all digests in descending date order."""
	digest_files = sorted(
		[f for f in digests_dir.glob("digest-*.html") if f.is_file()],
		key=lambda x: x.stem[7:17],  # Sort by date part of filename
		reverse=True
	)

	context = {
		'digests': [
			{
				'filename': f.name,
				'date': f.stem[7:17]
			}
			for f in digest_files
		]
	}

	template_path = Path(__file__).parent / 'templates' / 'index.html.mustache'
	with open(template_path, 'r', encoding='utf-8') as f:
		template = f.read()

	return chevron.render(template, context)