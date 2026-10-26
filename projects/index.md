---
title: Projects
nav:
  order: 2
  tooltip: Research themes and applications
---

# {% include icon.html icon="fa-solid fa-wrench" %}Projects

Explore the research themes behind our work in precision engineering, robotics, and intelligent manufacturing. Each topic links to our publication library, where you can search for related methods and applications.

{% include tags.html tags="control, planning, robotics, manufacturing, perception" %}

{% include search-info.html %}

{% include section.html %}

## Core Research Themes

{% include list.html component="card" data="projects" filter="group == 'featured'" %}

{% include section.html %}

## Related Directions

{% include list.html component="card" data="projects" filter="!group" style="small" %}
