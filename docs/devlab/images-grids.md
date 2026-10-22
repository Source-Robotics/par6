# Images, figures and grids

Every image on the site can be clicked to zoom (the `glightbox` plugin).

## Size and alignment

![Placeholder](../assets/placeholder-hero.png){ width="320" }

```markdown
![Placeholder](../assets/placeholder-hero.png){ width="320" }
```

![Placeholder](../assets/placeholder-hero.png){ align=right width="260" }

Text wraps around an image aligned to the right or the left. A short paragraph beside a photo of the connector
or the screw being described reads better than a full-width image followed by the text, as long as the paragraph
is long enough to reach past the image, which this one is.

```markdown
![Placeholder](../assets/placeholder-hero.png){ align=right width="260" }

Text wraps around an image aligned to the right ...
```

## Figure with a numbered caption

<figure markdown="span">
  ![Figure 4.3: the arm on the base plate](../assets/placeholder-hero.png){ width="480" }
  <figcaption>Figure 4.3: The arm on the base plate, connector panel facing the box</figcaption>
</figure>

```markdown
<figure markdown="span">
  ![Figure 4.3: the arm on the base plate](../assets/placeholder-hero.png){ width="480" }
  <figcaption>Figure 4.3: The arm on the base plate, connector panel facing the box</figcaption>
</figure>
```

This is the manuals' figure form: numbered per chapter, captioned, zoomable.

## Light and dark variants

![Logo](../assets/logo_new_2.png#only-dark){ width="200" }
![Icon](../assets/Icon2.png#only-light){ width="80" }

Two images, one per colour scheme; toggle the scheme in the header to see the other.

```markdown
![Logo](../assets/logo_new_2.png#only-dark){ width="200" }
![Icon](../assets/Icon2.png#only-light){ width="80" }
```

## Lazy loading

`{ loading=lazy }` on any image defers it until it scrolls into view — for long pages with many photos.

## Card grid

<div class="grid cards" markdown>

-   :material-robot-industrial:{ .lg .middle } __PAR6 Hardware Manual__

    ---

    Safety, specifications, installation, operation and maintenance of the arm.

    [:octicons-arrow-right-24: Open](../par6/index.md)

-   :material-developer-board:{ .lg .middle } __Control Box Manual__

    ---

    The box's hardware, the software setup, configuration and operation.

    [:octicons-arrow-right-24: Open](../rcb/index.md)

-   :simple-python:{ .lg .middle } __Programming Guide__

    ---

    Every way to command the robot, from the Python API to the real-time interface.

    [:octicons-arrow-right-24: Open](../programming/index.md)

-   :material-monitor-dashboard:{ .lg .middle } __Dashboard Guide__

    ---

    The operator web interface, tab by tab.

    [:octicons-arrow-right-24: Open](../dashboard/index.md)

</div>

```markdown
<div class="grid cards" markdown>

-   :material-robot-industrial:{ .lg .middle } __PAR6 Hardware Manual__

    ---

    Safety, specifications, installation, operation and maintenance of the arm.

    [:octicons-arrow-right-24: Open](../par6/index.md)

-   :material-developer-board:{ .lg .middle } __Control Box Manual__

    ---

    ...

</div>
```

A card grid is the natural landing page for a tab that holds several manuals (End Effectors) or for a chapter
page listing its sub-pages.

## Generic grid (any blocks side by side)

<div class="grid" markdown>

!!! note "Left cell"
    An admonition in a grid cell.

```python title="Right cell"
robot.move_joints(0, -60, 60, 0, 0, 0)
```

| Joint | Reference |
|---|---|
| J1–J5 | endstop |
| J6 | Hall sensor |

> A quote in the fourth cell.

</div>

```markdown
<div class="grid" markdown>

!!! note "Left cell"
    An admonition in a grid cell.

```python title="Right cell"
...
```

</div>
```
