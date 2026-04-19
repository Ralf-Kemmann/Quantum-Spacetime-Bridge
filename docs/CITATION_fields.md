# CITATION.cff Field Description

## Purpose of this file

This document describes the fields used in the repository file `CITATION.cff`.

Its purpose is to provide a quick and transparent overview of the citation metadata structure for reviewers, users, and maintainers. In a numerics-heavy or method-structured project, such a field description helps make the metadata logic easier to inspect, validate, and extend.

## File role in the project

`CITATION.cff` is the repository-level citation metadata file. It tells users and services how this repository should be cited and which core bibliographic metadata belong to the current project state.

## Field list

1. **`cff-version`**  
   **Field type:** String  
   **Field description:** Version of the Citation File Format specification used by this file.

2. **`message`**  
   **Field type:** String  
   **Field description:** Human-readable note shown to users, explaining how the repository should be cited.

3. **`title`**  
   **Field type:** String  
   **Field description:** Main title of the repository or project.

4. **`abstract`**  
   **Field type:** String (multiline allowed)  
   **Field description:** Short descriptive summary of the repository content and its current scientific status.

5. **`type`**  
   **Field type:** String  
   **Field description:** Type of the citable object. In the current file, this is set to `software`.

6. **`authors`**  
   **Field type:** List of objects  
   **Field description:** Structured list of project authors associated with the repository.

7. **`authors[].family-names`**  
   **Field type:** String  
   **Field description:** Family name / surname of the listed author.

8. **`authors[].given-names`**  
   **Field type:** String  
   **Field description:** Given name / first name of the listed author.

9. **`authors[].orcid`**  
   **Field type:** String (URL)  
   **Field description:** ORCID identifier of the listed author in URL form.

10. **`authors[].affiliation`**  
    **Field type:** String  
    **Field description:** Institutional or professional affiliation of the listed author.

11. **`repository-code`**  
    **Field type:** String (URL)  
    **Field description:** Direct URL of the source code repository.

12. **`url`**  
    **Field type:** String (URL)  
    **Field description:** Main public URL associated with the repository or project.

13. **`license`**  
    **Field type:** String  
    **Field description:** License identifier or license status string for the repository metadata. In the current file, `NOASSERTION` indicates that no final license statement has yet been asserted in the citation metadata.

14. **`keywords`**  
    **Field type:** List of strings  
    **Field description:** Thematic keywords that characterize the project and improve discoverability.

15. **`version`**  
    **Field type:** String  
    **Field description:** Version label of the repository state represented by the citation file.

16. **`date-released`**  
    **Field type:** Date string (`YYYY-MM-DD`)  
    **Field description:** Release date associated with the current citation-recorded repository version.

## Notes for maintenance

- If new citation-relevant metadata fields are added to `CITATION.cff`, they should also be documented here.
- If the repository license is later fixed by an actual `LICENSE` file, the `license` field in `CITATION.cff` should be updated accordingly.
- If additional authors, identifiers, or publication links are added, the corresponding nested fields should be extended in this document as well.

## Maintenance principle

The goal of this companion file is not only technical completeness, but also long-term readability. A repository that includes explicit field descriptions is easier to review, maintain, and reuse in later formal project stages.
