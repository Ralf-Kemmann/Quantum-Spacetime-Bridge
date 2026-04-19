# Public Links Field Description

## Purpose of this file

This document describes the conceptual fields used in `links/public-links.md`.

Its purpose is to make the outward-facing link architecture easier to inspect, maintain, and extend.

## Field list

1. **`repository_link`**  
   **Field type:** URL string  
   **Field description:** Main public code and project repository link.

2. **`publication_title`**  
   **Field type:** String  
   **Field description:** Official title of the current public publication associated with the project.

3. **`publication_url`**  
   **Field type:** URL string or placeholder string  
   **Field description:** Direct public link to the current publication page.

4. **`orcid_link`**  
   **Field type:** URL string  
   **Field description:** Public ORCID identifier link of the project lead.

5. **`repository_reference_targets`**  
   **Field type:** List of strings  
   **Field description:** Repository files or sections that are expected to reference the public links index.

6. **`maintenance_rule`**  
   **Field type:** String  
   **Field description:** Rule describing when and how new stable public links should be added.

7. **`future_additions`**  
   **Field type:** List of strings  
   **Field description:** Anticipated future public resources that may later be linked from the project.
