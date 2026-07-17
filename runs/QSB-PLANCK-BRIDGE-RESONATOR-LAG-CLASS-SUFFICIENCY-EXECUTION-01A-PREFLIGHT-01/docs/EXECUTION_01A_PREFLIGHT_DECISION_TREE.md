# Execution 01A Preflight Decision Tree

1. Are required input runs present?
   - Yes.

2. Are source files and generated contract artifacts present?
   - Yes.

3. Do schemas parse?
   - Yes.

4. Does K_candidate hash match the documented expected hash?
   - Yes.

5. Are claim boundaries preserved?
   - Yes.

6. Are preflight-critical placeholders resolved?
   - No.

Decision:

```text
no_go_requires_contract_value_review
```
