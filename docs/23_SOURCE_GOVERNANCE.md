# Source Governance

## Authority

The complete project source register remains the authoritative record for:

- datasets
- research papers
- documentation
- software references
- licenses
- versions
- access dates
- source-to-file mappings

The README should contain only a curated bibliography.

## Citation policy

Every external technical claim or academic claim must have a traceable source.

The project distinguishes:

1. essential references;
2. relevant supporting papers;
3. implementation/documentation sources;
4. project links.

## README policy

Keep the public README bibliography intentionally small.

Current structure:

```text
Level 1 — Essential references
Level 2 — Relevant supporting papers
```

The complete register should not be duplicated into the README.

## Dataset policy

Never commit a raw dataset merely for convenience.

Record:

- source URL
- DOI where available
- license
- access date
- version
- checksum
- preprocessing decisions

## Research integrity

Do not:

- fabricate results;
- hide failed experiments;
- present optional models as executed;
- describe probabilities as truth;
- claim production validation from local smoke tests.
