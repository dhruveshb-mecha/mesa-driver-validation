// Flutter GPU micro-benchmark for the Mecha Comet (standard Flutter Linux/GTK embedder, Impeller GLES or Skia GL).
// Usage: gpu_bench SCENE [N] [SECONDS]      e.g. gpu_bench blur 8 8
// Prints one line:  FLUTTERBENCH {"scene":..,"n":..,"fps":..,"raster_p50_ms":..,"raster_p95_ms":..,"total_p95_ms":..,"frames":..,"size":"WxH"}
// then exits. Scenes: circles gradients shadows blur opacity text images list clip
import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math' as math;
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

late String scene;
late int n;
late double secs;
final List<FrameTiming> timings = [];
ui.Image? tex;

Future<void> main(List<String> args) async {
  WidgetsFlutterBinding.ensureInitialized();
  scene = args.isNotEmpty ? args[0] : 'circles';
  n = args.length > 1 ? int.parse(args[1]) : 20;
  secs = args.length > 2 ? double.parse(args[2]) : 8;
  if (scene == 'images') tex = await makeTexture();
  SchedulerBinding.instance.addTimingsCallback((t) => timings.addAll(t));
  runApp(const BenchApp());
  Timer(Duration(milliseconds: (secs * 1000).round() + 1500), finish);
}

Future<ui.Image> makeTexture() async {
  final px = Uint8List(128 * 128 * 4);
  for (var y = 0; y < 128; y++) {
    for (var x = 0; x < 128; x++) {
      final i = (y * 128 + x) * 4;
      px[i] = (x * 2) & 255; px[i + 1] = (y * 2) & 255; px[i + 2] = ((x + y) * 3) & 255; px[i + 3] = 255;
    }
  }
  final c = Completer<ui.Image>();
  ui.decodeImageFromPixels(px, 128, 128, ui.PixelFormat.rgba8888, c.complete);
  return c.future;
}

void finish() {
  // drop 1.0 s warm-up (first ~60 frames), compute stats
  final ts = timings.length > 60 ? timings.sublist(math.min(60, timings.length ~/ 4)) : timings;
  double ms(Duration d) => d.inMicroseconds / 1000.0;
  double pct(List<double> v, double p) { v.sort(); return v.isEmpty ? 0 : v[math.min(v.length - 1, (v.length * p).floor())]; }
  final raster = ts.map((t) => ms(t.rasterDuration)).toList();
  final total = ts.map((t) => ms(t.totalSpan)).toList();
  final build = ts.map((t) => ms(t.buildDuration)).toList();
  double fps = 0;
  if (ts.length > 1) {
    final span = ts.last.timestampInMicroseconds(ui.FramePhase.rasterFinish) - ts.first.timestampInMicroseconds(ui.FramePhase.rasterFinish);
    fps = (ts.length - 1) / (span / 1e6);
  }
  final v = WidgetsBinding.instance.platformDispatcher.views.first;
  final sz = v.physicalSize;
  stdout.writeln('FLUTTERBENCH ${jsonEncode({
    'scene': scene, 'n': n, 'fps': double.parse(fps.toStringAsFixed(1)),
    'raster_p50_ms': double.parse(pct(List.of(raster), .5).toStringAsFixed(1)),
    'raster_p95_ms': double.parse(pct(List.of(raster), .95).toStringAsFixed(1)),
    'build_p95_ms': double.parse(pct(List.of(build), .95).toStringAsFixed(1)),
    'total_p95_ms': double.parse(pct(List.of(total), .95).toStringAsFixed(1)),
    'frames': ts.length, 'size': '${sz.width.toInt()}x${sz.height.toInt()}'})}');
  exit(0);
}

class BenchApp extends StatelessWidget {
  const BenchApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(debugShowCheckedModeBanner: false, home: Scaffold(body: Bench()));
}

class Bench extends StatefulWidget {
  const Bench({super.key});
  @override
  State<Bench> createState() => _BenchState();
}

class _BenchState extends State<Bench> with SingleTickerProviderStateMixin {
  late final AnimationController c = AnimationController(vsync: this, duration: const Duration(seconds: 6))..repeat();
  @override
  void dispose() { c.dispose(); super.dispose(); }

  // position of item i at animation value t, inside w x h
  Offset pos(int i, double t, Size s) {
    final a = t * 2 * math.pi * 2 + i * 0.37;
    final rx = (s.width / 2 - 70) * ((i % 7) + 1) / 7, ry = (s.height / 2 - 60) * ((i % 5) + 1) / 5;
    return Offset(s.width / 2 + math.cos(a) * rx, s.height / 2 + math.sin(a) * ry);
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, box) {
      final s = box.biggest;
      return AnimatedBuilder(animation: c, builder: (context, _) {
        final t = c.value;
        switch (scene) {
          case 'circles':
            return CustomPaint(size: s, painter: CirclesPainter(n * 20, t));
          case 'list':
            return ListView.builder(
              controller: ScrollController(initialScrollOffset: t * 20000),
              itemCount: 100000,
              itemBuilder: (_, i) => ListTile(leading: CircleAvatar(child: Text('$i')), title: Text('Item number $i'), subtitle: const Text('subtitle text that is a bit longer'), trailing: const Icon(Icons.chevron_right)));
          case 'text':
            return Stack(children: [for (var i = 0; i < n; i++) Positioned(left: pos(i, t, s).dx - 60, top: pos(i, t, s).dy - 10, child: Text('The quick brown fox $i jumps over', style: const TextStyle(fontSize: 16)))]);
          default:
            return Stack(children: [for (var i = 0; i < n; i++) Positioned(left: pos(i, t, s).dx - 50, top: pos(i, t, s).dy - 35, child: item(i, t))]);
        }
      });
    });
  }

  Widget item(int i, double t) {
    final col = HSVColor.fromAHSV(1, (i * 37 + t * 360) % 360, .7, .9).toColor();
    switch (scene) {
      case 'gradients':
        return Container(width: 110, height: 80, decoration: BoxDecoration(borderRadius: BorderRadius.circular(8),
          gradient: LinearGradient(colors: [col, Colors.blue, Colors.green], begin: Alignment.topLeft, end: Alignment.bottomRight),
          backgroundBlendMode: BlendMode.srcOver),
          foregroundDecoration: BoxDecoration(gradient: RadialGradient(colors: [Colors.white.withOpacity(.7), Colors.transparent])));
      case 'shadows':
        return Container(width: 90, height: 60, decoration: BoxDecoration(color: col, borderRadius: BorderRadius.circular(10),
          boxShadow: const [BoxShadow(color: Colors.black54, blurRadius: 14, offset: Offset(0, 6)), BoxShadow(color: Colors.black38, blurRadius: 4)]));
      case 'blur':
        return ClipRRect(borderRadius: BorderRadius.circular(12), child: BackdropFilter(filter: ui.ImageFilter.blur(sigmaX: 6, sigmaY: 6),
          child: Container(width: 100, height: 70, color: col.withOpacity(.35))));
      case 'opacity':
        return Opacity(opacity: .7, child: Container(width: 140, height: 100, decoration: BoxDecoration(color: col, borderRadius: BorderRadius.circular(24), border: Border.all(color: Colors.yellow, width: 3))));
      case 'clip':
        return ClipRRect(borderRadius: BorderRadius.circular(30), child: Container(width: 120, height: 90, decoration: BoxDecoration(gradient: LinearGradient(colors: [col, Colors.white])), child: const Center(child: Text('clip'))));
      case 'images':
        return RawImage(image: tex, width: 128, height: 128, scale: .8 + .4 * math.sin(t * 12 + i));
      default:
        return Container(width: 80, height: 60, color: col);
    }
  }
}

class CirclesPainter extends CustomPainter {
  final int count; final double t;
  CirclesPainter(this.count, this.t);
  @override
  void paint(Canvas canvas, Size s) {
    final p = Paint();
    final cx = s.width / 2, cy = s.height / 2;
    for (var i = 0; i < count; i++) {
      final a = t * 6.28 + i * 0.157, r = 20.0 + i * 0.35;
      p.color = HSVColor.fromAHSV(.7, (i * 3.0 + t * 360) % 360, .8, .9).toColor();
      canvas.drawCircle(Offset(cx + math.cos(a) * r, cy + math.sin(a) * r), 3.0 + (i % 7), p);
    }
  }
  @override
  bool shouldRepaint(CirclesPainter o) => true;
}
