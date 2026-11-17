#!/usr/bin/python3
"""Generate the deterministic input files used by the app workflows (nothing here is downloaded). Usage: make_testdata.py OUTDIR
  images/   4 large JPEG/PNG photos-like images (6000x4000, 4000x3000 ...) for Loupe / Nautilus thumbnails
  files/    400 mixed files + 12 sub folders for Nautilus scrolling / thumbnailing
  doc.pdf   60 page PDF with text, vector graphics and gradients (Papers)
  long.txt  30000 line text/source file (Text Editor)
  page.html CSS animation + canvas2D + WebGL page (Epiphany)"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter
out = sys.argv[1]; random.seed(7)
for d in ("images", "files"): os.makedirs(f"{out}/{d}", exist_ok=True)

def photo(w, h, seed):
    r = random.Random(seed)
    im = Image.new("RGB", (w, h)); px = im.load()
    sm = Image.new("RGB", (64, 48))
    for x in range(64):
        for y in range(48):
            sm.putpixel((x, y), (int(127 + 120 * math.sin(x / 9 + seed)), int(127 + 120 * math.sin(y / 7 + seed * 2)), int(127 + 120 * math.sin((x + y) / 11))))
    im = sm.resize((w, h), Image.BICUBIC)
    d = ImageDraw.Draw(im)
    for _ in range(400):
        x, y, s = r.randrange(w), r.randrange(h), r.randrange(20, 300)
        d.ellipse([x, y, x + s, y + s], outline=(r.randrange(256), r.randrange(256), r.randrange(256)), width=r.randrange(2, 9))
    return im.filter(ImageFilter.GaussianBlur(1.2))
for i, (w, h) in enumerate([(6000, 4000), (4000, 3000), (6000, 4000), (3000, 2000)]):
    photo(w, h, i + 1).save(f"{out}/images/photo{i + 1}.jpg", quality=90)
photo(4000, 3000, 9).save(f"{out}/images/photo5.png")
for i in range(400):
    sub = f"{out}/files/dir{i % 12:02d}"; os.makedirs(sub, exist_ok=True)
    k = i % 4
    if k == 0: photo(800, 600, 100 + i).save(f"{sub}/img_{i:03d}.jpg", quality=80)
    elif k == 1: open(f"{sub}/note_{i:03d}.txt", "w").write(("lorem ipsum %d\n" % i) * 200)
    elif k == 2: photo(400, 400, 200 + i).save(f"{sub}/pic_{i:03d}.png")
    else: open(f"{sub}/data_{i:03d}.csv", "w").write("\n".join(",".join(str(random.random()) for _ in range(8)) for _ in range(100)))
with open(f"{out}/long.txt", "w") as f:
    for i in range(30000): f.write(f"static int compute_{i}(int a, int b)  /* line {i} */ {{ return (a * {i % 97 + 1}) ^ (b + {i}); }}\n")
import cairo
s = cairo.PDFSurface(f"{out}/doc.pdf", 595, 842); c = cairo.Context(s)
for p in range(60):
    g = cairo.LinearGradient(0, 0, 595, 842); g.add_color_stop_rgb(0, (p % 7) / 7, 0.3, 0.8); g.add_color_stop_rgb(1, 0.9, (p % 5) / 5, 0.2)
    c.set_source(g); c.rectangle(0, 0, 595, 120); c.fill()
    c.set_source_rgb(1, 1, 1); c.select_font_face("Sans", 0, 1); c.set_font_size(34); c.move_to(30, 75); c.show_text(f"Test document - page {p + 1}")
    c.set_source_rgb(0, 0, 0); c.select_font_face("Sans", 0, 0); c.set_font_size(11)
    for l in range(48): c.move_to(30, 150 + l * 14); c.show_text(f"Line {l} of page {p + 1}: the quick brown fox jumps over the lazy dog 0123456789")
    for k in range(30):
        c.set_source_rgba(random.random(), random.random(), random.random(), 0.35); c.arc(random.randrange(595), random.randrange(150, 842), random.randrange(10, 80), 0, 6.3); c.fill()
    c.show_page()
s.finish()
open(f"{out}/page.html", "w").write("""<!doctype html><meta charset=utf-8><title>gpu page</title><style>
body{margin:0;background:#111;color:#eee;font:16px sans-serif}.b{position:absolute;width:60px;height:60px;border-radius:50%;animation:m 3s ease-in-out infinite alternate}
@keyframes m{from{transform:translate(0,0) scale(1)}to{transform:translate(300px,200px) scale(1.8) rotate(180deg)}}canvas{position:absolute;left:0;top:240px}
#gl{top:520px}</style><body><div id=hud>CSS animation + canvas2D + WebGL</div>
<script>for(let i=0;i<40;i++){let d=document.createElement('div');d.className='b';d.style.left=(i*13)+'px';d.style.top=(60+i*3)+'px';d.style.background='hsl('+(i*9)+',80%,55%)';d.style.animationDelay=(i*-.07)+'s';document.body.appendChild(d)}</script>
<canvas id=c width=520 height=260></canvas><canvas id=gl width=520 height=300></canvas><script>
const x=document.getElementById('c').getContext('2d');let t=0;
(function f(){t++;x.clearRect(0,0,520,260);for(let i=0;i<300;i++){x.fillStyle='hsl('+((i*3+t*2)%360)+',80%,60%)';x.beginPath();x.arc(260+Math.cos(i*.2+t*.03)*i*.8,130+Math.sin(i*.31+t*.02)*i*.4,6,0,7);x.fill()}requestAnimationFrame(f)})();
const g=document.getElementById('gl').getContext('webgl2');if(g){const vs='#version 300 es\\nin vec2 p;uniform float t;out vec2 v;void main(){v=p;gl_Position=vec4(p,0,1);}';
const fs='#version 300 es\\nprecision highp float;in vec2 v;uniform float t;out vec4 o;void main(){vec2 z=v*1.6;float k=0.;for(int i=0;i<60;i++){z=vec2(z.x*z.x-z.y*z.y,2.*z.x*z.y)+vec2(.35*cos(t),.35*sin(t*1.3));if(dot(z,z)>4.)break;k+=1.;}o=vec4(vec3(k/60.,k/30.,.5+.5*sin(k+t)),1);}';
function sh(ty,s){const h=g.createShader(ty);g.shaderSource(h,s);g.compileShader(h);return h}const pr=g.createProgram();g.attachShader(pr,sh(g.VERTEX_SHADER,vs));g.attachShader(pr,sh(g.FRAGMENT_SHADER,fs));g.linkProgram(pr);g.useProgram(pr);
const b=g.createBuffer();g.bindBuffer(g.ARRAY_BUFFER,b);g.bufferData(g.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),g.STATIC_DRAW);const l=g.getAttribLocation(pr,'p');g.enableVertexAttribArray(l);g.vertexAttribPointer(l,2,g.FLOAT,false,0,0);
const u=g.getUniformLocation(pr,'t');let q=0;(function r(){q+=.02;g.uniform1f(u,q);g.drawArrays(g.TRIANGLE_STRIP,0,4);requestAnimationFrame(r)})();document.getElementById('hud').textContent+=' | WebGL2 OK: '+g.getParameter(g.VERSION)}else document.getElementById('hud').textContent+=' | WebGL2 NOT AVAILABLE';
</script>""")
print("testdata written to", out)
