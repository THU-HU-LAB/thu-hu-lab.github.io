---
---

# HU-LAB

HU-LAB is a research group led by Professor Chuxiong Hu in the Department of Mechanical Engineering at Tsinghua University. We advance robotics and intelligent manufacturing through research in precision motion control, optimal trajectory planning, safe coordination of multiple robots, robotic perception, and learning for manipulation and assembly. Our work brings together control theory, optimization, machine learning, and mechatronic system design to connect fundamental methods with practical engineering. Working closely with industry, we develop algorithms, software, and robotic systems for semiconductor manufacturing equipment, CNC machining, robotic additive and subtractive manufacturing, automated dispensing and assembly, and intelligent railway maintenance.

{%
  include button.html
  type="docs"
  link="https://greene-lab.gitbook.io/lab-website-template-docs"
%}
{%
  include button.html
  type="github"
  text="Website source"
  link="THU-HU-LAB/thu-hu-lab.github.io"
%}

{% include section.html %}

## Highlights

{% capture text %}

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

{%
  include button.html
  link="research"
  text="See our publications"
  icon="fa-solid fa-arrow-right"
  flip=true
  style="bare"
%}

{% endcapture %}

{%
  include feature.html
  image="images/photo.jpg"
  link="research"
  title="Our Research"
  text=text
%}

{% capture text %}

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

{%
  include button.html
  link="projects"
  text="Browse our projects"
  icon="fa-solid fa-arrow-right"
  flip=true
  style="bare"
%}

{% endcapture %}

{%
  include feature.html
  image="images/photo.jpg"
  link="projects"
  title="Our Projects"
  flip=true
  style="bare"
  text=text
%}

{% capture text %}

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

{%
  include button.html
  link="team"
  text="Meet our team"
  icon="fa-solid fa-arrow-right"
  flip=true
  style="bare"
%}

{% endcapture %}

{%
  include feature.html
  image="images/photo.jpg"
  link="team"
  title="Our Team"
  text=text
%}
