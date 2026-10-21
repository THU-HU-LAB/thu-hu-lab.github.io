---
title: Team
nav:
  order: 3
  tooltip: About our team
---

# {% include icon.html icon="fa-solid fa-users" %}Team

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

{% include section.html %}

{% include portrait.html lookup="huchuxiong" hide_affiliation=true %}
{% include portrait.html lookup="wangze" hide_affiliation=true %}
{% include portrait.html lookup="jinzhao" hide_affiliation=true %}
{% include portrait.html lookup="yanjizhou" hide_affiliation=true %}
{% include portrait.html lookup="yujichuan" hide_affiliation=true %}
{% include portrait.html lookup="wangyunan" hide_affiliation=true %}
{% include portrait.html lookup="zhaoyueyao" hide_affiliation=true %}

{% include section.html background="images/background.jpg" dark=true %}

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

{% include section.html %}

{% capture content %}

{% include figure.html image="images/photo.jpg" %}
{% include figure.html image="images/photo.jpg" %}
{% include figure.html image="images/photo.jpg" %}

{% endcapture %}

{% include grid.html style="square" content=content %}
