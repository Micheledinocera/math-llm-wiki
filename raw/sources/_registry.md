# Source registry

One row per source in this folder, appended by `/ingest`. This is the only file in `raw/` the agent may edit: it appends rows, and changes `reliability` only on the author's request.

The id is `<firstauthor><year>` in lowercase (`a`, `b`… on clashes). The source file is `raw/sources/<id>.md`, its wiki page `wiki/sources/src-<id>.md`. `reliability` is one of `standard`, `refereed`, `preprint`, `informal` and must match the `src-` page.

| id | citation | reliability | file | ingested |
| --- | --- | --- | --- | --- |
