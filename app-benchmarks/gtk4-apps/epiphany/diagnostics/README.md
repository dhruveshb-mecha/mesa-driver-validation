# Epiphany diagnostics: why no page loads

Every screenshot shows the same thing: tab title "Blank page", empty content, load bar stuck near the start. Run by hand on the board (not part of the sweep), `epiphany --incognito-mode <url>`, 14 s wait, then `grim`.

| file | what was loaded / changed |
|---|---|
| 1-trivial-local-html.png | `file:///.../trivial.html` (`<h1>hello</h1>`) |
| 2-https-example-org.png | `https://example.org` (the board has internet access) |
| 3-WEBKIT_DISABLE_DMABUF_RENDERER=1.png | DMABUF renderer off |
| 4-WEBKIT_DISABLE_COMPOSITING_MODE=1.png | accelerated compositing off |
| 5-cairo+no-compositing+no-dmabuf.png | GSK_RENDERER=cairo plus both of the above |
| 6-explicit-DBUS_SESSION_BUS_ADDRESS.png | session bus address set explicitly (it was already set) |

Result: nothing changes. No Mesa/EGL error, no kernel event, no coredump. `Web process crashed` was logged once in an earlier run (16:46:53, page.html, after the scroll phase) and not in the three clean runs above. Not tried: disabling WebKit's sandbox (deliberately skipped, it is a security control). So the cause is **unknown and not shown to be GPU related**; it needs a WebKitGTK-side investigation.
