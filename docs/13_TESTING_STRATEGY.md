# Testing Strategy

## Test levels

### Unit tests

Test:

- data validation
- label mapping
- text normalization
- feature transformations
- model factories
- evaluation metrics
- drift mathematics

### Integration tests

Test:

```text
dashboard
→ API
→ artifact
→ prediction
```

### End-to-end test

A full test shall:

1. start the API;
2. load a known test artifact;
3. submit a known article;
4. verify schema;
5. verify that a result is returned;
6. verify that the dashboard can render the response.

## Regression tests

Maintain fixed synthetic fixtures for:

- empty text
- punctuation-only text
- long text
- invalid payloads
- unknown labels
- missing fields
- near-duplicate examples

## Leakage tests

Tests shall verify that:

- test data does not fit TF-IDF;
- calibration does not fit on test labels;
- validation is used only according to documented rules;
- unsupervised transforms are not accidentally refit on held-out data.

## API security tests

Cover:

- oversized payload
- malformed JSON
- invalid content type
- control characters
- rate/concurrency controls
- readiness failure
- sanitized errors

## Performance smoke tests

The goal is not a formal production benchmark. Establish a repeatable smoke test for:

- single prediction latency
- bounded batch latency
- memory stability
