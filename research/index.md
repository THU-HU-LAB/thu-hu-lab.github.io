---
title: Research
nav:
  order: 1
  tooltip: Published works
---

# {% include icon.html icon="fa-solid fa-microscope" %}Research

课题组论文与研究成果。可搜索题名、作者或 DOI；点击成员主页中的链接，可查看与该成员关联的成果。

预印本、会议论文、期刊论文、书籍章节和勘误已分别标注。已核实的预印本与正式版本合并展示；有公开全文的记录提供 PDF 链接。

{% include section.html %}

## Highlighted


{% include section.html %}

## All publications

{% assign total_publications = site.data.citations | size %}
共 {{ total_publications }} 条成果记录。

{% include search-box.html %}

{% include search-info.html %}

{% include list.html data="citations" component="citation" %}
