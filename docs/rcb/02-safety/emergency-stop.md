---
status: draft
---

# Emergency stop wiring

*Stub.* <!-- sources: planning/01_structure_proposal_v1.md §4 -->

## The two channels { #the-two-channels }

The connector panel has two E-stop channels, each a pair of terminals in the two-by-two block to the right of the
numbered terminals: E-Stop 1 is E2 and E4, E-Stop 2 is E1 and E3 (E2 and E1 on top, E4 and E3 below). How the runtime
reads them depends on the board:

| Board | Channels the runtime reads |
|---|---|
| PCB v1 | E-Stop 1 only. E-Stop 2 always reads pressed, a fault in the board's layout, so the runtime ignores it |
| PCB v2 | Both, cross-checked: either channel pressed stops the robot. The two disagreeing for more than 200 ms is a channel fault, logged as `E-stop CHANNEL FAULT` and treated as pressed |

!!! warning "PCB v1: wire the E-stop to E-Stop 1"
    On a PCB v1 board, connect the E-stop button to E-Stop 1, terminals E2 and E4. A button on E-Stop 2 alone stops
    nothing.

## The board's version { #pcb-version }

The board does not report its version. The runtime takes it from `config/system.xml`, and that number decides which
channels it reads:

```xml
<control_box>
    <pcb_version>1</pcb_version>
</control_box>
```

Keep it right: a wrong number gives the wrong E-stop policy. The version is on the label inside the box
([Versions & compatibility](../../support/versions.md)).

The runtime's pin map, `docs/pin_map.md` at <!-- version-link: runtime -->, has every terminal of the connector panel.
