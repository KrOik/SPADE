# SPADE: An Intelligent Software Platform for Antimicrobial Peptide Discovery

## 1. Project Background

Antimicrobial peptide research depends on scattered publications, heterogeneous databases and ad‑hoc spreadsheets, making routine questions—what sequences have evidence against a target organism, what properties matter for a design constraint, what toxicity signals are reported—slow to answer and hard to reproduce across teams. SPADE was started to gather dependable AMP data with provenance into a single entry point, normalize key fields into a consistent schema, and provide a simple path from query to inspection to interpretation.

The scope reflects day‑to‑day needs: a curated index cross‑referenced from peer‑reviewed literature, a workflow that stays within three surfaces (Search, Peptide Card, AMP Visualization), and transparent scoring governed by program/weights_config.yaml so efficacy, stability, synthesis and toxicity can be reviewed with the same assumptions across projects. Updates are reproducible and auditable, and users can see how the dataset evolves with each release.

Operations favor reliability with low maintenance overhead: a static frontend and a lightweight Flask backend keep the attack surface small and make deployments predictable; hosting on Netlify provides global CDN distribution, automatic HTTPS and preview environments for reviewing changes before publication, while SPADE’s architecture remains provider‑agnostic and centered on maintainability, security and retrieval efficiency.

## 2. Project Vision and Motivation

SPADE serves researchers and industry R&D teams who need dependable antimicrobial peptide (AMP) data that can be queried quickly and applied directly in discovery workflows, bringing curated entries, clear structures and practical filters together so everyday questions can be answered without wrestling with format inconsistencies or scattered sources.

The index covers more than 46,000 peptides, cross‑referenced from PubMed and peer‑reviewed literature, and consolidated into a single schema that preserves provenance while standardizing key fields to support consistent queries.

Data quality is maintained through a streamlined yet rigorous pipeline that combines human judgment and automation: records are cross‑checked across sources and harmonized by manual curation when fields conflict, duplicates are removed by exact sequence and normalized name matching with additional near‑duplicate flags from edit‑distance checks, and each release undergoes stratified random sampling to verify correctness and relevance; we publish per‑release quality indicators—manual cross‑check counts, automated deduplication rate, and sampling coverage—together with the index so users can see how the dataset is maintained over time.

To match common usage habits, the website supports Chinese, English, Japanese, German and Spanish, and the search interface keeps interactions consistent with a left‑side panel for filters and a results table that updates immediately as conditions change; filters name the fields users care about—ID, name, sequence length, activity type and target organism, physicochemical attributes such as net charge and hydrophobicity, and predicted structural features—so typical queries can be expressed in one pass.

A typical combination might target antifungal activity against Candida albicans with net charge above +2 and a hydrophobicity range suited to membrane interaction, and the operational path keeps analysis close to the task by setting conditions on the Search page, reading the updated results table, and opening the peptide’s card to examine consolidated details in a single view.

## 3. A Guided Tour of the SPADE Platform

The website follows a workflow that aligns with how people actually use AMP data: you begin on the Home page to understand the modules and reach the key entry points, you set conditions on the Search page with a left‑side filter panel and watch the results table update as you refine queries, and you open a peptide’s card to read consolidated details in one place so the transition from overview to inspection does not interrupt the task.

The Home page introduces the platform and provides direct navigation to Search, Peptide Card, AMP Visualization, Tools and Statistics; images on this page are placeholders that will be replaced later.

![Placeholder: Home Page](source/img/usage/mainpage.jpg "Placeholder: Home Page")

The Search page implements multi‑dimensional filtering over a curated index of more than 46,000 peptides, with fields that match common habits—ID, name, sequence length, activity type and target organism, physicochemical attributes such as net charge and hydrophobicity, and predicted structural features—so typical queries can be expressed in one pass and the table of results remains the primary data display for scanning and selection.

![Placeholder: Search Page](source/img/usage/mainpage.jpg "Placeholder: Search Page")

The Peptide Card presents a single peptide in a structured view that brings together sequence, derived properties, measured activities, predicted structure, and literature references; the card is designed as the second data display page in the workflow, and clicking from the results table to the card keeps context while shifting from list‑level screening to item‑level verification.

AMP Visualization focuses on scoring views that aid interpretation, exposing plots such as hydrophobicity profiles and simple 2D structure predictions alongside a score summary of how a peptide aligns with desired properties. Score composition is transparent and follows program/weights_config.yaml: efficacy, stability, synthesis and toxicity contribute at weighted proportions, with sub‑weights covering MIC with a synergy bonus, half‑life, pH/thermal stability, protease sensitivity, disulfide count, sequence length and rare amino acids, and toxicity indicators such as Boman score, cytotoxicity and hemolysis. Range parameters—GRAVY optimal −0.2 to 0.1, maximum sequence length 30, minimum hydrophobicity 0.4, optimal disulfide count 4—use the same configuration.

![Placeholder: Peptide Card + AMP Visualization](source/img/usage/mainpage.jpg "Placeholder: Peptide Card + AMP Visualization")

The Tools page links to internal scripts and selected external utilities for alignment, structure prediction and toxicity analysis, and the Statistics page offers interactive charts that summarize global distributions—sequence lengths, activity types and target organisms—so dataset shape can be reviewed before or after focused filtering.

![Placeholder: Tools Page + Statistics Page](source/img/usage/mainpage.jpg "Placeholder: Tools Page + Statistics Page")

## 4. User Guide: Getting Started with SPADE

### Search & Filtering
Set filters on the left‑side panel; the results table updates instantly as you refine.

### Peptide Information
Open the Peptide Card to read sequence, properties, activities, structure and references in one consolidated view.

### Scoring Visualization
AMP Visualization shows hydrophobicity profiles, simple 2D structure predictions, and a score summary governed by program/weights_config.yaml.

Glossary
- results table: the main list view on the Search page that updates instantly with filters.
- left‑side filter panel: the control area on the Search page for Basic, Activity, Structure conditions.
- Peptide Card: the consolidated single‑peptide view with sequence, properties, activity, structure, references.
- AMP Visualization: the page for hydrophobicity profiles, simple structure predictions, and the score summary.
- score summary: the weighted overview of efficacy, stability, synthesis, and toxicity following program/weights_config.yaml.
- Flask backend: the lightweight server processes specific tasks behind the static frontend.
- program/weights_config.yaml: the configuration file specifying weights and ranges used in scoring and visualization.

## 5. Design Philosophy and Architectural Overview

SPADE favors maintainability through a simple, modular architecture: the frontend is a static site (HTML/CSS/vanilla JS) and specific processing tasks are handled by a lightweight Flask backend. Pages are loosely coupled, and data, UI, and configuration are separated into predictable file boundaries—for example, the curated index under data/index, result artifacts under data/result, and scoring parameters in program/weights_config.yaml—so new features can be added by introducing a page and wiring it into navigation without disturbing existing modules.

Management and retrieval efficiency are achieved by a pre‑compiled JSON index (data/index/peptide_index.json) combined with client‑side filtering and incremental loading. Large datasets are delivered in chunks (see js/chunks/) to keep first paint fast and reduce memory pressure, and the Search page updates results immediately as conditions change so screening stays on the same surface. Index generation and optimization scripts (program/generate_extended_index.py, program/optimize_data.py) keep refreshes reproducible; outputs are versioned under data/result to simplify rollbacks and audits.

Security is addressed by minimizing the attack surface and constraining server responsibilities. The static frontend avoids long‑lived servers at the edge, sensitive operations are limited to well‑scoped endpoints, and common abuse patterns are mitigated by protective scripts where appropriate. SPADE is deployed on Netlify to inherit CDN distribution and automatic HTTPS, with preview environments useful for reviewing changes before publication; the provider’s role is operational and supporting, while SPADE’s design choices remain the primary basis for security and reliability.

