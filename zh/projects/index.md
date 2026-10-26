---
title: 研究方向
permalink: /zh/projects/
nav:
  order: 2
  tooltip: 研究主题与应用
---

# {% include icon.html icon="fa-solid fa-wrench" %}研究方向 {#projects}

了解课题组在精密工程、机器人与智能制造领域的研究主题。点击各方向可进入论文库，查找相关方法与应用。

{% include tags.html tags="control, planning, robotics, manufacturing, perception" %}
{% include search-info.html %}
{% include section.html %}

## 核心研究主题 {#core-research-themes}

{% include list.html component="card" data="projects" filter="group == 'featured'" %}
{% include section.html %}

## 相关研究方向 {#related-directions}

{% include list.html component="card" data="projects" filter="!group" style="small" %}
