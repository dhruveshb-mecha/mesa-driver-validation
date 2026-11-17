/* Standard GTK4 demo app for the Comet (C, built on the laptop, see build.sh).
 *   gtk4_demo widgets [SECS]   - GTK "getting started"-style app: header bar, buttons, entry, switch, scale,
 *                                progress bar, spinner, scrolling GtkListView with 10000 rows (auto-scrolling)
 *   gtk4_demo glarea  [SECS]   - GtkGLArea (the standard GTK GL widget) drawing 3D rotating cubes with GLES 3.0 shaders
 * Prints: GTK4DEMO {"mode","renderer","gl","frames","fps","size"} and exits after SECS (default 10). */
#include <gtk/gtk.h>
#include <epoxy/gl.h>
#include <math.h>

static const char *mode = "widgets"; static double secs = 10; static GtkWidget *win; static int frames; static gint64 t0, tfirst;
static char glinfo[256] = "n/a";

static gboolean finish(gpointer d) {
  GtkNative *n = gtk_widget_get_native(win); GskRenderer *r = gtk_native_get_renderer(n);
  double el = (g_get_monotonic_time() - tfirst) / 1e6;
  g_print("GTK4DEMO {\"mode\":\"%s\",\"renderer\":\"%s\",\"gl\":\"%s\",\"frames\":%d,\"fps\":%.1f,\"size\":\"%dx%d\"}\n", mode,
          r ? G_OBJECT_TYPE_NAME(r) : "?", glinfo, frames, frames / el, gtk_widget_get_width(win), gtk_widget_get_height(win));
  g_application_quit(g_application_get_default()); return G_SOURCE_REMOVE;
}
static gboolean tick(GtkWidget *w, GdkFrameClock *c, gpointer d) { if (!frames) tfirst = g_get_monotonic_time(); frames++; return G_SOURCE_CONTINUE; }

/* ---- GL area ---- */
static GLuint prog, vao, vbo; static GLint u_mvp;
static const char *VS = "#version 300 es\nlayout(location=0) in vec3 p; layout(location=1) in vec3 n; uniform mat4 mvp; out vec3 vn;\n"
  "void main(){ vn=n; gl_Position=mvp*vec4(p,1.0);} ";
static const char *FS = "#version 300 es\nprecision mediump float; in vec3 vn; out vec4 c;\n"
  "void main(){ float l=max(dot(normalize(vn),normalize(vec3(.4,.8,.6))),0.0); c=vec4(vec3(.3,.6,.9)*(.25+.75*l),1.0);} ";
static GLuint sh(GLenum t, const char *s) { GLuint x = glCreateShader(t); glShaderSource(x, 1, &s, NULL); glCompileShader(x);
  GLint ok; glGetShaderiv(x, GL_COMPILE_STATUS, &ok); if (!ok) { char b[512]; glGetShaderInfoLog(x, 512, NULL, b); g_printerr("shader: %s\n", b); } return x; }
static void mul(float *o, const float *a, const float *b) { for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) { o[j*4+i]=0; for (int k = 0; k < 4; k++) o[j*4+i]+=a[k*4+i]*b[j*4+k]; } }
static void gl_realize(GtkGLArea *a) {
  gtk_gl_area_make_current(a); if (gtk_gl_area_get_error(a)) { g_printerr("GLAREA ERROR\n"); return; }
  snprintf(glinfo, sizeof glinfo, "%s | %s", glGetString(GL_RENDERER), glGetString(GL_VERSION));
  prog = glCreateProgram(); glAttachShader(prog, sh(GL_VERTEX_SHADER, VS)); glAttachShader(prog, sh(GL_FRAGMENT_SHADER, FS)); glLinkProgram(prog);
  u_mvp = glGetUniformLocation(prog, "mvp");
  float f[6][4][3] = {0}; /* cube: 6 faces x (pos) ; normals derived */
  static const float N[6][3] = {{0,0,1},{0,0,-1},{1,0,0},{-1,0,0},{0,1,0},{0,-1,0}};
  float v[36 * 6]; int vi = 0;
  for (int fc = 0; fc < 6; fc++) { const float *n = N[fc]; float u[3], w[3];
    int ax = fc / 2; int a1 = (ax + 1) % 3, a2 = (ax + 2) % 3; for (int i=0;i<3;i++){u[i]=0;w[i]=0;} u[a1]=1; w[a2]=1;
    float s = (fc % 2) ? -1 : 1; (void)f;
    float q[4][2] = {{-1,-1},{1,-1},{1,1},{-1,1}}; int idx[6] = {0,1,2,0,2,3};
    for (int k = 0; k < 6; k++) { float *c = q[idx[k]]; for (int i = 0; i < 3; i++) { v[vi++] = n[i]*0.5f + (u[i]*c[0] + w[i]*c[1])*0.5f*s*(i==ax?0:1) + (i==ax?0:0); } for (int i=0;i<3;i++) v[vi++]=n[i]; } }
  glGenVertexArrays(1, &vao); glBindVertexArray(vao); glGenBuffers(1, &vbo); glBindBuffer(GL_ARRAY_BUFFER, vbo);
  glBufferData(GL_ARRAY_BUFFER, sizeof v, v, GL_STATIC_DRAW);
  glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, (void *)0); glEnableVertexAttribArray(0);
  glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, (void *)12); glEnableVertexAttribArray(1);
}
static gboolean gl_render(GtkGLArea *a, GdkGLContext *ctx) {
  double t = (g_get_monotonic_time() - t0) / 1e6; int w = gtk_widget_get_width(GTK_WIDGET(a)), h = gtk_widget_get_height(GTK_WIDGET(a));
  glClearColor(.05f, .05f, .08f, 1); glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); glEnable(GL_DEPTH_TEST);
  glUseProgram(prog); glBindVertexArray(vao);
  for (int i = 0; i < 60; i++) {
    float a1 = t * (0.6f + (i % 5) * 0.2f) + i, ca = cosf(a1), sa = sinf(a1), cb = cosf(a1*.7f), sb = sinf(a1*.7f);
    float ry[16] = {ca,0,-sa,0, 0,1,0,0, sa,0,ca,0, 0,0,0,1}, rx[16] = {1,0,0,0, 0,cb,sb,0, 0,-sb,cb,0, 0,0,0,1};
    float tr[16] = {.18f,0,0,0, 0,.18f*w/h,0,0, 0,0,.18f,0, cosf(i*.5f+t*.3f)*.8f, sinf(i*.31f+t*.2f)*.8f, 0, 1};
    float m1[16], m2[16]; mul(m1, rx, ry); mul(m2, tr, m1); glUniformMatrix4fv(u_mvp, 1, GL_FALSE, m2); glDrawArrays(GL_TRIANGLES, 0, 36);
  }
  return TRUE;
}
static gboolean gl_anim(GtkWidget *w, GdkFrameClock *c, gpointer d) { gtk_gl_area_queue_render(GTK_GL_AREA(w)); return G_SOURCE_CONTINUE; }

/* ---- widgets ---- */
static gboolean scroll_it(gpointer sw) { GtkAdjustment *a = gtk_scrolled_window_get_vadjustment(sw);
  gtk_adjustment_set_value(a, fmod(gtk_adjustment_get_value(a) + 40, gtk_adjustment_get_upper(a))); return G_SOURCE_CONTINUE; }
static gboolean spin_it(gpointer p) { GtkWidget **w = p; static double v; v += 0.01; gtk_progress_bar_set_fraction(GTK_PROGRESS_BAR(w[0]), fmod(v, 1.0));
  gtk_range_set_value(GTK_RANGE(w[1]), fmod(v * 100, 100)); return G_SOURCE_CONTINUE; }
static void setup_item(GtkSignalListItemFactory *f, GtkListItem *li) { GtkWidget *b = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
  gtk_box_append(GTK_BOX(b), gtk_image_new_from_icon_name("folder-symbolic")); gtk_box_append(GTK_BOX(b), gtk_label_new("")); gtk_box_append(GTK_BOX(b), gtk_check_button_new());
  gtk_list_item_set_child(li, b); }
static void bind_item(GtkSignalListItemFactory *f, GtkListItem *li) { GtkWidget *b = gtk_list_item_get_child(li); GtkWidget *l = gtk_widget_get_next_sibling(gtk_widget_get_first_child(b));
  gtk_label_set_text(GTK_LABEL(l), gtk_string_object_get_string(gtk_list_item_get_item(li))); }
static void activate(GtkApplication *app, gpointer d) {
  win = gtk_application_window_new(app); gtk_window_set_title(GTK_WINDOW(win), "GTK4 demo (Mecha Comet)");
  GtkWidget *root;
  if (!strcmp(mode, "glarea")) { root = gtk_gl_area_new(); gtk_gl_area_set_required_version(GTK_GL_AREA(root), 3, 0); gtk_gl_area_set_has_depth_buffer(GTK_GL_AREA(root), TRUE);
    gtk_gl_area_set_allowed_apis(GTK_GL_AREA(root), GDK_GL_API_GLES);
    g_signal_connect(root, "realize", G_CALLBACK(gl_realize), NULL); g_signal_connect(root, "render", G_CALLBACK(gl_render), NULL);
    gtk_widget_add_tick_callback(root, gl_anim, NULL, NULL); }
  else {
    GtkWidget *hb = gtk_header_bar_new(); gtk_window_set_titlebar(GTK_WINDOW(win), hb); gtk_header_bar_pack_end(GTK_HEADER_BAR(hb), gtk_button_new_with_label("Menu"));
    GtkWidget *box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 8); gtk_widget_set_margin_top(box,8); gtk_widget_set_margin_start(box,8); gtk_widget_set_margin_end(box,8);
    GtkWidget *row = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
    gtk_box_append(GTK_BOX(row), gtk_button_new_with_label("Button")); gtk_box_append(GTK_BOX(row), gtk_entry_new()); gtk_box_append(GTK_BOX(row), gtk_switch_new());
    GtkWidget *sp = gtk_spinner_new(); gtk_spinner_set_spinning(GTK_SPINNER(sp), TRUE); gtk_box_append(GTK_BOX(row), sp); gtk_box_append(GTK_BOX(box), row);
    static GtkWidget *w2[2]; w2[0] = gtk_progress_bar_new(); w2[1] = gtk_scale_new_with_range(GTK_ORIENTATION_HORIZONTAL, 0, 100, 1);
    gtk_box_append(GTK_BOX(box), w2[0]); gtk_box_append(GTK_BOX(box), w2[1]); g_timeout_add(16, spin_it, w2);
    GListStore *st = g_list_store_new(GTK_TYPE_STRING_OBJECT); for (int i = 0; i < 10000; i++) { char b[64]; snprintf(b, 64, "Row %d - some file name.txt", i); GtkStringObject *o = gtk_string_object_new(b); g_list_store_append(st, o); }
    GtkListItemFactory *f = gtk_signal_list_item_factory_new(); g_signal_connect(f, "setup", G_CALLBACK(setup_item), NULL); g_signal_connect(f, "bind", G_CALLBACK(bind_item), NULL);
    GtkWidget *lv = gtk_list_view_new(GTK_SELECTION_MODEL(gtk_single_selection_new(G_LIST_MODEL(st))), f);
    GtkWidget *sw = gtk_scrolled_window_new(); gtk_scrolled_window_set_child(GTK_SCROLLED_WINDOW(sw), lv); gtk_widget_set_vexpand(sw, TRUE); gtk_box_append(GTK_BOX(box), sw);
    g_timeout_add(16, scroll_it, sw); root = box; }
  gtk_window_set_child(GTK_WINDOW(win), root); gtk_window_present(GTK_WINDOW(win)); t0 = g_get_monotonic_time();
  gtk_widget_add_tick_callback(win, tick, NULL, NULL); g_timeout_add((guint)((secs + 1.5) * 1000), finish, NULL);
}
int main(int argc, char **argv) {
  if (argc > 1) mode = argv[1]; if (argc > 2) secs = atof(argv[2]);
  GtkApplication *app = gtk_application_new("org.mecha.gtk4demo", G_APPLICATION_NON_UNIQUE); g_signal_connect(app, "activate", G_CALLBACK(activate), NULL);
  return g_application_run(G_APPLICATION(app), 1, argv);
}
