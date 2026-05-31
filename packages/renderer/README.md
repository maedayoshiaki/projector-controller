# projector-controller-renderer

The Rust/wgpu GPU renderer binary used by
[`projector-controller`](https://github.com/maedayoshiaki/projector-controller)
for realtime frame projection (`RealtimeProjection`).

This package ships a single executable, `projector-controller-renderer`, which
`projector-controller` launches as a subprocess and feeds frames over a localhost
TCP protocol. You normally do not install this package directly — instead install
the realtime extra:

```bash
pip install "projector-controller[realtime]"
```

Installing this package places the renderer binary on your environment's `PATH`
(the venv's `Scripts`/`bin` directory), where `projector-controller` discovers it
automatically.

See the main project for usage, architecture, and licensing.
