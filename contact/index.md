---
title: Contact
nav:
  order: 5
  tooltip: Email and affiliation
---

# {% include icon.html icon="fa-regular fa-envelope" %}Contact

For research collaboration, graduate study, postdoctoral opportunities, or other inquiries about HU-LAB, please contact Professor Chuxiong Hu. You can also find individual contact details on our team members' profiles.

{%
  include button.html
  type="email"
  text="cxhu@tsinghua.edu.cn"
  link="cxhu@tsinghua.edu.cn"
%}
{%
  include button.html
  type="website"
  text="Department of Mechanical Engineering"
  link="https://me.tsinghua.edu.cn/info/1118/3390.htm"
%}
{%
  include button.html
  type="address"
  text="Tsinghua University"
  tooltip="Find Tsinghua University on Google Maps"
  link="https://www.google.com/maps/search/?api=1&query=Tsinghua+University"
%}

{% include section.html %}

{% capture col1 %}

## Research Inquiries

Tell us about your research interests and how they relate to our work in precision motion control, robotics, planning, or intelligent manufacturing.

{% endcapture %}

{% capture col2 %}

## Joining the Group

Prospective students and postdoctoral researchers are welcome to get in touch by email. Please include a brief introduction and your relevant academic or research background.

{% endcapture %}

{% include cols.html col1=col1 col2=col2 %}

{% include section.html dark=true %}

{% capture col1 %}
**HU-LAB**<br>
Research in precision engineering, robotics, and intelligent manufacturing.
{% endcapture %}

{% capture col2 %}
**Affiliation**<br>
Department of Mechanical Engineering<br>
Tsinghua University
{% endcapture %}

{% capture col3 %}
**Email**<br>
[cxhu@tsinghua.edu.cn](mailto:cxhu@tsinghua.edu.cn)
{% endcapture %}

{% include cols.html col1=col1 col2=col2 col3=col3 %}
