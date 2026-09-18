# Frozen snapshots

See [docs/CORPUS_DJANGO.md](../docs/CORPUS_DJANGO.md) for the django/django
pre-AI freeze (`merged:<2021-01-01`, **6125** rows, frozen 2026-09-18).

On DGX the immutable files live under `data/frozen/` (gitignored `*.sqlite`):

- `ace_patterns_django_pre2021_6125.sqlite`
- `ace_patterns_django_pre2021_6125.sqlite.bak`

The live harvest DB (`ace_patterns.sqlite`) stays mutable for multi-repo upserts.
