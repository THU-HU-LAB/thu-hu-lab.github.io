---
title: Research
nav:
  order: 1
  tooltip: Published works
---

# {% include icon.html icon="fa-solid fa-microscope" %}Research

Explore the group's publications and research outputs. Search by title, author, or DOI, or follow the publication link on a member's profile to view their associated works.

This page lists verified journal articles, conference papers, book chapters, and corrections with formal publication records. Links to publicly available full texts are provided where available.

{% include section.html %}

## Highlighted


{% include section.html %}

## All publications

{% assign published_filter = "metadata_verified == true && ['journal', 'conference', 'book-chapter', 'correction'].include?(publication_type)" %}
{% assign total_publications = site.data.citations | data_filter: published_filter | size %}
{{ total_publications }} verified publication records.

{% include search-box.html %}

{% include search-info.html %}

{% include list.html data="citations" component="citation" filter=published_filter %}
