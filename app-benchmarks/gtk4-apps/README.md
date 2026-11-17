# GTK4 application track

Mainstream GNOME / libadwaita applications that people use daily, run on the board's Mesa 27 (GTK 4.22.5, libadwaita 1.9.4, Fedora packages, not rebuilt). Each folder = one application, with the workflow, the per-phase frame rates for three renderer modes and two attempts, health checks and screenshots.

Renderer modes: `default` (what a user gets; GTK 4.22 picks `GskGLRenderer`), `gl` (`GSK_RENDERER=gl`, same renderer, explicit), `cairo` (`GSK_RENDERER=cairo`, CPU control).

| app | verdict | what stands out |
|---|---|---|
| [text-editor](text-editor/README.md) | **performance problem** | GL 4-8 fps vs Cairo 34 fps when scrolling a long file (4-8x slower); typing 5 vs 24 fps |
| [loupe](loupe/README.md) | PASS | GL ~5x faster than Cairo zooming a 6000x4000 JPEG (18 vs 3-4 fps) |
| [font-viewer](font-viewer/README.md) | PASS | GL faster than Cairo scrolling the font list (26 vs 14-18 fps) |
| [nautilus](nautilus/README.md) | PASS | GL = Cairo within noise on thumbnail grid and list view |
| [papers](papers/README.md) | PASS | same in GL and Cairo |
| [maps](maps/README.md) | PASS (does it render) | static view, network tiles, low fps by nature |
| [calculator](calculator/README.md) / [characters](characters/README.md) / [clocks](clocks/README.md) | PASS | no differences between renderers |
| [epiphany](epiphany/README.md) | **not working, cause unknown** | loads no page at all (even a one-line HTML file); GPU toggles do not change it |

Across all 60 runs: no GPU hang, no crash, no llvmpipe, no etnaviv/drm kernel message.

How the numbers are taken: see `../tools/app_drive.py` (frames = Wayland surface commits of the app's main surface) and `../tools/profiles.py` (the workflow of each app). Static screens correctly show ~0 fps.
