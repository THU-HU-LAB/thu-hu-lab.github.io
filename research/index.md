---
title: Research
nav:
  order: 1
  tooltip: Published works
---

# {% include icon.html icon="fa-solid fa-microscope" %}Research

课题组论文与研究成果。可搜索题名、作者或 DOI；点击成员主页中的链接，可查看与该成员关联的成果。

本页展示已核实正式出版记录的期刊论文、会议论文、书籍章节和勘误；有公开全文的记录提供 PDF 链接。

{% include section.html %}

## Highlighted


{% include section.html %}

## All publications

{% assign published_filter = "metadata_verified == true && ['journal', 'conference', 'book-chapter', 'correction'].include?(publication_type)" %}
{% assign total_publications = site.data.citations | data_filter: published_filter | size %}
共 {{ total_publications }} 条正式出版记录。

{% include search-box.html %}

{% include search-info.html %}

{% include list.html data="citations" component="citation" filter=published_filter %}
