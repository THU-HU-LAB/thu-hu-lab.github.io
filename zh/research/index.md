---
title: 研究成果
permalink: /zh/research/
nav:
  order: 1
  tooltip: 已发表论文与研究成果
---

# {% include icon.html icon="fa-solid fa-microscope" %}研究成果 {#research}

浏览课题组的论文与研究成果。可以按标题、作者或 DOI 搜索，也可以从成员主页进入，查看与该成员关联的论文。

本页收录已核验正式发表信息的期刊论文、会议论文、书籍章节与勘误，并在可获取时提供公开全文链接。论文标题、作者和出版信息保留原文。

{% include section.html %}

## 代表性成果 {#highlighted}

{% include section.html %}

## 全部论文 {#all-publications}

{% assign published_filter = "metadata_verified == true && ['journal', 'conference', 'book-chapter', 'correction'].include?(publication_type)" %}
{% assign total_publications = site.data.citations | data_filter: published_filter | size %}
共 {{ total_publications }} 条已核验的正式发表记录。

{% include search-box.html %}
{% include search-info.html %}
{% include list.html data="citations" component="citation" filter=published_filter %}
