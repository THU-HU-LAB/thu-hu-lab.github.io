---
title: Blog
nav:
  order: 4
  tooltip: Lab news and research updates
---

# {% include icon.html icon="fa-solid fa-feather-pointed" %}Blog

This page is intended for lab news, research notes, and announcements. The example posts below illustrate the website's blog format; they are not reports of past lab events.

{% include section.html %}

{% include search-box.html %}

{% include tags.html tags=site.tags %}

{% include search-info.html %}

{% include list.html data="posts" component="post-excerpt" %}
