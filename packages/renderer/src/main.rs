use std::{
    env,
    error::Error,
    io,
    net::{TcpListener, TcpStream},
    sync::Arc,
    thread,
};

use winit::event_loop::{EventLoop, EventLoopBuilder};

mod inbox;
mod protocol;
mod render;

use inbox::{Backpressure, FrameInbox};
use protocol::{FitMode, ProtocolMessage};
use render::{RendererConfig, RendererEvent};

fn main() -> Result<(), Box<dyn Error>> {
    let args = Args::parse(env::args().skip(1))?;
    let event_loop = EventLoopBuilder::<RendererEvent>::with_user_event().build()?;

    // Authoritative monitor list for the realtime path: this is the same winit
    // enumeration that `render::run` indexes with `--display`, so the numbers printed
    // here map 1:1 to what `--display N` selects (unlike pygame's separate list).
    if args.list_monitors {
        print_monitors(&event_loop);
        return Ok(());
    }

    let inbox = Arc::new(FrameInbox::new(args.backpressure));
    let proxy = event_loop.create_proxy();
    let listener = TcpListener::bind(&args.bind)?;
    let local_addr = listener.local_addr()?;
    let accept_inbox = Arc::clone(&inbox);
    thread::spawn(move || accept_frames(listener, accept_inbox, proxy));

    render::run(args.into_renderer_config(), event_loop, local_addr, inbox)
}

fn accept_frames(
    listener: TcpListener,
    inbox: Arc<FrameInbox>,
    proxy: winit::event_loop::EventLoopProxy<RendererEvent>,
) {
    for stream in listener.incoming() {
        match stream {
            Ok(mut stream) => {
                if let Err(error) = read_stream(&mut stream, &inbox, &proxy) {
                    eprintln!("renderer IPC error: {error}");
                }
            }
            Err(error) => {
                eprintln!("renderer accept error: {error}");
                break;
            }
        }
    }
}

fn read_stream(
    stream: &mut TcpStream,
    inbox: &FrameInbox,
    proxy: &winit::event_loop::EventLoopProxy<RendererEvent>,
) -> io::Result<()> {
    while let Some(message) = protocol::read_message(stream)? {
        match message {
            ProtocolMessage::Frame(frame) => {
                // May block in All mode (back-pressuring the producer over TCP) or
                // overwrite the pending frame in Latest mode. Either way, wake the loop
                // to drain it; one signal per frame keeps a 1:1 frame->present in All.
                inbox.push(frame);
                let _ = proxy.send_event(RendererEvent::FrameReady);
            }
            ProtocolMessage::Shutdown => {
                let _ = proxy.send_event(RendererEvent::Shutdown);
                return Ok(());
            }
        }
    }
    Ok(())
}

#[derive(Debug)]
struct Args {
    bind: String,
    display: usize,
    fullscreen: bool,
    width: u32,
    height: u32,
    x: Option<i32>,
    y: Option<i32>,
    fit_mode: FitMode,
    backpressure: Backpressure,
    list_monitors: bool,
}

impl Args {
    fn parse(mut values: impl Iterator<Item = String>) -> Result<Self, Box<dyn Error>> {
        let mut args = Self {
            bind: "127.0.0.1:0".to_string(),
            display: 0,
            fullscreen: false,
            width: 1280,
            height: 720,
            x: None,
            y: None,
            fit_mode: FitMode::Contain,
            backpressure: Backpressure::Latest,
            list_monitors: false,
        };

        while let Some(arg) = values.next() {
            match arg.as_str() {
                "--bind" => args.bind = next_value(&mut values, "--bind")?,
                "--display" => args.display = next_value(&mut values, "--display")?.parse()?,
                "--fullscreen" => args.fullscreen = true,
                "--list-monitors" => args.list_monitors = true,
                "--width" => args.width = next_value(&mut values, "--width")?.parse()?,
                "--height" => args.height = next_value(&mut values, "--height")?.parse()?,
                "--x" => args.x = Some(next_value(&mut values, "--x")?.parse()?),
                "--y" => args.y = Some(next_value(&mut values, "--y")?.parse()?),
                "--fit-mode" => {
                    args.fit_mode = parse_fit_mode(&next_value(&mut values, "--fit-mode")?)?;
                }
                "--backpressure" => {
                    args.backpressure =
                        parse_backpressure(&next_value(&mut values, "--backpressure")?)?;
                }
                "--help" | "-h" => {
                    print_help();
                    std::process::exit(0);
                }
                _ => return Err(format!("unknown argument: {arg}").into()),
            }
        }

        if args.width == 0 || args.height == 0 {
            return Err("width and height must be positive".into());
        }
        Ok(args)
    }

    fn into_renderer_config(self) -> RendererConfig {
        RendererConfig {
            display: self.display,
            fullscreen: self.fullscreen,
            width: self.width,
            height: self.height,
            x: self.x,
            y: self.y,
            fit_mode: self.fit_mode,
        }
    }
}

fn next_value(
    values: &mut impl Iterator<Item = String>,
    flag: &str,
) -> Result<String, Box<dyn Error>> {
    values
        .next()
        .ok_or_else(|| format!("missing value for {flag}").into())
}

fn print_monitors(event_loop: &EventLoop<RendererEvent>) {
    for (index, monitor) in event_loop.available_monitors().enumerate() {
        let position = monitor.position();
        let size = monitor.size();
        let name = monitor.name().unwrap_or_default();
        // Tab-separated so monitor names with spaces survive parsing; name is last.
        println!(
            "MONITOR\t{index}\t{}\t{}\t{}\t{}\t{}\t{name}",
            position.x,
            position.y,
            size.width,
            size.height,
            monitor.scale_factor(),
        );
    }
}

fn parse_fit_mode(value: &str) -> Result<FitMode, Box<dyn Error>> {
    match value {
        "contain" => Ok(FitMode::Contain),
        "cover" => Ok(FitMode::Cover),
        "stretch" => Ok(FitMode::Stretch),
        "native" => Ok(FitMode::Native),
        _ => Err(format!("unsupported fit mode: {value}").into()),
    }
}

fn parse_backpressure(value: &str) -> Result<Backpressure, Box<dyn Error>> {
    match value {
        "latest" => Ok(Backpressure::Latest),
        "all" => Ok(Backpressure::All),
        _ => Err(format!("unsupported backpressure mode: {value}").into()),
    }
}

fn print_help() {
    println!(
        "\
projector-controller-renderer

Options:
  --bind HOST:PORT       TCP bind address for frame IPC (default: 127.0.0.1:0)
  --list-monitors       print monitors (index/x/y/width/height/scale/name) and exit
  --display N           target monitor index (default: 0)
  --fullscreen          open borderless fullscreen on the target monitor
  --width N             window width in physical pixels (default: 1280)
  --height N            window height in physical pixels (default: 720)
  --x N                 window x in desktop coordinates
  --y N                 window y in desktop coordinates
  --fit-mode MODE       contain, cover, stretch, or native (default: contain)
  --backpressure MODE   latest = drop stale frames, keep newest (default);
                        all = render every frame, pacing the producer when busy
"
    );
}
