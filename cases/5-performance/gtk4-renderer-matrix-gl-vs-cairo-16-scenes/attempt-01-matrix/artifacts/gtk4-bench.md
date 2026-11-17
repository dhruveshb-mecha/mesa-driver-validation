# GTK4 renderer benchmark (Cairo = CPU, GL = GPU via etnaviv)

| scene | n | window | cairo fps | gl fps | gl/cairo | gl p95 ms | gl max ms |
|---|---|---|---|---|---|---|---|
| widgets | 10 | full (540x620) | 49.6 | 25.9 | 0.52x | 48.3 | 66.5 |
| widgets | 40 | full (540x620) | 26.7 | 6.7 | 0.25x | 165.9 | 167.1 |
| text | 10 | full (830x620) | 16.5 | 30.3 | 1.84x | 67.0 | 130.0 |
| text | 40 | full | 5.0 | rc=-11 such file or directory.
libGL: Warning in /usr/share/drirc.d/00-msm-defaults.conf line -1, column -1: unknown device attribute: device_name.
libGL: Can't open configuration file /etc/drirc: No such file or directory.
libGL: Can't open configuration file /home/mecha/.drirc: No such file or directory. | - | - | - |
| shadows | 10 | full (540x620) | 11.6 | 6.5 | 0.56x | 217.7 | 1182.6 |
| shadows | 40 | full (540x620) | 3.5 | 2.0 | 0.57x | 1149.4 | 1149.4 |
| gradients | 10 | full (540x620) | 10.6 | 5.5 | 0.52x | 200.3 | 200.3 |
| gradients | 40 | full (558x620) | 3.3 | 1.5 | 0.45x | 749.9 | 749.9 |
| rounded | 10 | full (540x620) | 20.7 | 17.1 | 0.83x | 66.7 | 82.8 |
| rounded | 40 | full (857x725) | 7.4 | 4.7 | 0.64x | 217.9 | 218.4 |
| textures | 10 | full (540x620) | 20.5 | 23.0 | 1.12x | 52.1 | 1150.0 |
| textures | 40 | full (787x909) | 6.3 | 10.1 | 1.60x | 151.6 | 162.7 |
| blur | 10 | full (540x620) | 21.8 | 3.2 | 0.15x | 1150.8 | 1150.8 |
| blur | 40 | full (541x629) | 6.5 | 1.2 | 0.18x | 931.0 | 931.0 |
| widgets | 40 | 640x480 (536x568) | 24.6 | 6.9 | 0.28x | 165.8 | 166.7 |
| shadows | 40 | 640x480 (536x543) | 3.2 | 2.1 | 0.66x | 499.9 | 499.9 |
| rounded | 40 | 640x480 (1221x807) | 6.5 | 4.5 | 0.69x | 233.3 | 384.1 |
