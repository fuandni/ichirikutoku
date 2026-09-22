# Question data split

The former inline `const Q=[...]` block in `index.html` is split into smaller JavaScript files.

- Questions: 75
- Chunks: 19
- Manifest: `question-data/manifest.json`
- Each chunk appends the original question objects to `window.Q`.
- Embedded problem images remain as data URIs inside their original question objects.

This keeps `index.html` small enough for repository tools/connectors to read, while preserving the existing browser behavior.
