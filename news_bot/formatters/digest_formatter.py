from datetime import datetime
from pathlib import Path


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


def generate_digest_index(digests_dir: Path) -> None:
	"""Generate an index.html file listing all digests in descending date order."""
	# Get all HTML files in the digests directory
	digest_files = sorted(
		[f for f in digests_dir.glob("digest-*.html") if f.is_file()],
		key=lambda x: x.stem[7:17],  # Sort by date part of filename
		reverse=True
	)

	# Generate HTML content
	html_content = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>News Digests</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #333; }}
            .digest-list {{ list-style: none; padding: 0; }}
            .digest-item {{ margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 4px; }}
            .digest-date {{ color: #666; font-size: 0.9em; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <h1>News Digests</h1>
        <ul class="digest-list">
    """

	for digest_file in digest_files:
		date = digest_file.stem[7:17]

		html_content += f"""
            <li class="digest-item">
                <a href="{digest_file.name}">Digest vom {date}</a>
            </li>
        """

	html_content += """
        </ul>
    </body>
    </html>
    """

	# Write index file
	index_path = digests_dir / "index.html"
	with open(index_path, 'w') as f:
		f.write(html_content)
	print(f"Index file updated at {index_path}")