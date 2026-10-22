# Admonitions

Callout boxes. The house rule uses three: Note (blue), Notice (orange, damage or data loss, rendered with the `warning` type) and Danger (red, injury); the rest are here to choose from.

## The twelve types

!!! note
    `note` — Identifies information that requires special consideration.

!!! abstract
    `abstract` — A summary at the top of a long page.

!!! info
    `info` — Background that is useful but not required.

!!! tip
    `tip` — A shortcut or a better way.

!!! success
    `success` — What a correct result looks like.

!!! question
    `question` — A question the reader may have at this point.

!!! warning
    `warning` — Must be respected to avoid damage to equipment or loss of data.

!!! failure
    `failure` — What a wrong result looks like.

!!! danger
    `danger` — Must be respected to avoid a potentially hazardous situation that could result in injury.

!!! bug
    `bug` — A known defect and its workaround.

!!! example
    `example` — A worked example.

!!! quote
    `quote` — A quotation.

```markdown
!!! note
    Identifies information that requires special consideration.

!!! warning
    Must be respected to avoid damage to equipment or loss of data.

!!! danger
    Must be respected to avoid a potentially hazardous situation that could result in injury.
```

The other types: `abstract`, `info`, `tip`, `success`, `question`, `failure`, `bug`, `example`, `quote`.

## Custom title, no title

!!! danger "Uncontrolled motion when the service stops"
    The drives let go about 0.1 s after the runtime stops; an unsupported arm falls under gravity.

    - Park the arm or support it before stopping the service.
    - Never stop the service while a program runs.

!!! note ""
    A note without a title bar.

```markdown
!!! danger "Uncontrolled motion when the service stops"
    The drives let go about 0.1 s after the runtime stops; an unsupported arm falls under gravity.

    - Park the arm or support it before stopping the service.
    - Never stop the service while a program runs.

!!! note ""
    A note without a title bar.
```

## Collapsible

??? info "Closed by default — click to open"
    Long reference material that most readers skip.

???+ tip "Open by default — can be closed"
    Shown expanded; the reader can fold it away.

```markdown
??? info "Closed by default — click to open"
    Long reference material that most readers skip.

???+ tip "Open by default — can be closed"
    Shown expanded; the reader can fold it away.
```

## Nested, and with content inside

!!! example "Homing from the API"
    The call blocks until the arm is homed:

    ```python
    robot.home(wait=True)
    ```

    !!! warning
        Nothing may restrict the joints during homing.

    | Joint | Reference |
    |---|---|
    | J1–J5 | endstop |
    | J6 | Hall sensor |

```markdown
!!! example "Homing from the API"
    The call blocks until the arm is homed:

    ```python
    robot.home(wait=True)
    ```

    !!! warning
        Nothing may restrict the joints during homing.

    | Joint | Reference |
    |---|---|
    | J1–J5 | endstop |
    | J6 | Hall sensor |
```

## Inline, beside the text

!!! info inline end "Inline, at the end"
    Sits to the right of the paragraph that follows it.

Text flows around an inline admonition. Useful for a short remark next to a procedure, such as which tool to use
or how long a step takes. The admonition must come *before* the paragraph it floats next to, and the paragraph
must be long enough to show the effect, which is why this one keeps going for a few more words than it needs.

!!! tip inline "Inline, at the start"
    Sits to the left.

The same, on the left. Both variants take any admonition type and any title.

```markdown
!!! info inline end "Inline, at the end"
    Sits to the right of the paragraph that follows it.

Text flows around an inline admonition ...

!!! tip inline "Inline, at the start"
    Sits to the left.
```
