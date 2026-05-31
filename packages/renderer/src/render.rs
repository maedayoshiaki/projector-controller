use std::{
    error::Error,
    io::{self, Write},
    net::SocketAddr,
};

use bytemuck::{Pod, Zeroable};
use wgpu::util::DeviceExt;
use winit::{
    dpi::{PhysicalPosition, PhysicalSize},
    event::{Event, WindowEvent},
    event_loop::{ControlFlow, EventLoop},
    window::{Fullscreen, Window, WindowBuilder},
};

use crate::protocol::{FitMode, FrameMessage, PixelFormat};

pub enum RendererEvent {
    Frame(FrameMessage),
    Shutdown,
}

#[derive(Clone, Debug)]
pub struct RendererConfig {
    pub display: usize,
    pub fullscreen: bool,
    pub width: u32,
    pub height: u32,
    pub x: Option<i32>,
    pub y: Option<i32>,
    pub fit_mode: FitMode,
}

pub fn run(
    config: RendererConfig,
    event_loop: EventLoop<RendererEvent>,
    ready_addr: SocketAddr,
) -> Result<(), Box<dyn Error>> {
    let monitor = event_loop
        .available_monitors()
        .nth(config.display)
        .or_else(|| event_loop.primary_monitor());

    let mut builder = WindowBuilder::new().with_title("projector-controller renderer");
    if config.fullscreen {
        builder = builder.with_fullscreen(Some(Fullscreen::Borderless(monitor.clone())));
    } else {
        builder = builder.with_inner_size(PhysicalSize::new(config.width, config.height));
        let position = if config.x.is_some() || config.y.is_some() {
            Some(PhysicalPosition::new(
                config.x.unwrap_or(0),
                config.y.unwrap_or(0),
            ))
        } else {
            monitor.as_ref().map(|monitor| {
                let monitor_position = monitor.position();
                let monitor_size = monitor.size();
                let x =
                    monitor_position.x + ((monitor_size.width as i32 - config.width as i32) / 2);
                let y =
                    monitor_position.y + ((monitor_size.height as i32 - config.height as i32) / 2);
                PhysicalPosition::new(x, y)
            })
        };
        if let Some(position) = position {
            builder = builder.with_position(position);
        }
    }

    let window = builder.build(&event_loop)?;
    let mut state = pollster::block_on(RenderState::new(&window, config.fit_mode))?;
    println!("READY {ready_addr}");
    io::stdout().flush()?;

    event_loop.run(move |event, target| {
        target.set_control_flow(ControlFlow::Wait);
        match event {
            Event::UserEvent(RendererEvent::Frame(frame)) => {
                state.upload_frame(frame);
                window.request_redraw();
            }
            Event::UserEvent(RendererEvent::Shutdown) => {
                target.exit();
            }
            Event::WindowEvent { event, .. } => match event {
                WindowEvent::CloseRequested => target.exit(),
                WindowEvent::Resized(size) => {
                    state.resize(size);
                    window.request_redraw();
                }
                WindowEvent::ScaleFactorChanged { .. } => {
                    state.resize(window.inner_size());
                    window.request_redraw();
                }
                WindowEvent::RedrawRequested => match state.render() {
                    Ok(()) => {}
                    Err(wgpu::SurfaceError::Lost | wgpu::SurfaceError::Outdated) => {
                        state.resize(state.size);
                    }
                    Err(wgpu::SurfaceError::OutOfMemory) => target.exit(),
                    Err(wgpu::SurfaceError::Timeout) => {}
                },
                _ => {}
            },
            _ => {}
        }
    })?;
    Ok(())
}

struct RenderState {
    surface: wgpu::Surface<'static>,
    device: wgpu::Device,
    queue: wgpu::Queue,
    config: wgpu::SurfaceConfiguration,
    size: PhysicalSize<u32>,
    pipeline: wgpu::RenderPipeline,
    texture_bind_group_layout: wgpu::BindGroupLayout,
    sampler: wgpu::Sampler,
    vertex_buffer: wgpu::Buffer,
    frame: Option<GpuFrame>,
    default_fit_mode: FitMode,
    active_fit_mode: FitMode,
}

impl RenderState {
    async fn new(window: &Window, default_fit_mode: FitMode) -> Result<Self, Box<dyn Error>> {
        let size = clamp_size(window.inner_size());
        let instance = wgpu::Instance::new(wgpu::InstanceDescriptor {
            backends: wgpu::Backends::all(),
            flags: wgpu::InstanceFlags::default(),
            dx12_shader_compiler: wgpu::Dx12Compiler::default(),
            gles_minor_version: wgpu::Gles3MinorVersion::Automatic,
        });
        let surface_target = unsafe { wgpu::SurfaceTargetUnsafe::from_window(window)? };
        let surface = unsafe { instance.create_surface_unsafe(surface_target)? };
        let adapter = instance
            .request_adapter(&wgpu::RequestAdapterOptions {
                power_preference: wgpu::PowerPreference::HighPerformance,
                force_fallback_adapter: false,
                compatible_surface: Some(&surface),
            })
            .await
            .ok_or("no suitable GPU adapter found")?;
        let (device, queue) = adapter
            .request_device(
                &wgpu::DeviceDescriptor {
                    label: Some("projector-controller device"),
                    required_features: wgpu::Features::empty(),
                    required_limits: wgpu::Limits::default(),
                },
                None,
            )
            .await?;

        let surface_caps = surface.get_capabilities(&adapter);
        let surface_format = surface_caps
            .formats
            .iter()
            .copied()
            .find(wgpu::TextureFormat::is_srgb)
            .unwrap_or(surface_caps.formats[0]);
        let present_mode = if surface_caps
            .present_modes
            .contains(&wgpu::PresentMode::Fifo)
        {
            wgpu::PresentMode::Fifo
        } else {
            surface_caps.present_modes[0]
        };
        let config = wgpu::SurfaceConfiguration {
            usage: wgpu::TextureUsages::RENDER_ATTACHMENT,
            format: surface_format,
            width: size.width,
            height: size.height,
            present_mode,
            alpha_mode: surface_caps.alpha_modes[0],
            view_formats: vec![],
            desired_maximum_frame_latency: 2,
        };
        surface.configure(&device, &config);

        let texture_bind_group_layout =
            device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
                label: Some("frame texture bind group layout"),
                entries: &[
                    wgpu::BindGroupLayoutEntry {
                        binding: 0,
                        visibility: wgpu::ShaderStages::FRAGMENT,
                        ty: wgpu::BindingType::Texture {
                            multisampled: false,
                            view_dimension: wgpu::TextureViewDimension::D2,
                            sample_type: wgpu::TextureSampleType::Float { filterable: true },
                        },
                        count: None,
                    },
                    wgpu::BindGroupLayoutEntry {
                        binding: 1,
                        visibility: wgpu::ShaderStages::FRAGMENT,
                        ty: wgpu::BindingType::Sampler(wgpu::SamplerBindingType::Filtering),
                        count: None,
                    },
                ],
            });
        let sampler = device.create_sampler(&wgpu::SamplerDescriptor {
            label: Some("frame sampler"),
            mag_filter: wgpu::FilterMode::Linear,
            min_filter: wgpu::FilterMode::Linear,
            ..Default::default()
        });
        let shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("frame shader"),
            source: wgpu::ShaderSource::Wgsl(include_str!("shader.wgsl").into()),
        });
        let pipeline_layout = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
            label: Some("frame pipeline layout"),
            bind_group_layouts: &[&texture_bind_group_layout],
            push_constant_ranges: &[],
        });
        let pipeline = device.create_render_pipeline(&wgpu::RenderPipelineDescriptor {
            label: Some("frame pipeline"),
            layout: Some(&pipeline_layout),
            vertex: wgpu::VertexState {
                module: &shader,
                entry_point: "vs_main",
                buffers: &[Vertex::layout()],
            },
            fragment: Some(wgpu::FragmentState {
                module: &shader,
                entry_point: "fs_main",
                targets: &[Some(wgpu::ColorTargetState {
                    format: surface_format,
                    blend: Some(wgpu::BlendState::REPLACE),
                    write_mask: wgpu::ColorWrites::ALL,
                })],
            }),
            primitive: wgpu::PrimitiveState {
                topology: wgpu::PrimitiveTopology::TriangleList,
                ..Default::default()
            },
            depth_stencil: None,
            multisample: wgpu::MultisampleState::default(),
            multiview: None,
        });
        let vertex_buffer = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("frame quad vertices"),
            contents: bytemuck::cast_slice(&empty_vertices()),
            usage: wgpu::BufferUsages::VERTEX | wgpu::BufferUsages::COPY_DST,
        });

        Ok(Self {
            surface,
            device,
            queue,
            config,
            size,
            pipeline,
            texture_bind_group_layout,
            sampler,
            vertex_buffer,
            frame: None,
            default_fit_mode,
            active_fit_mode: default_fit_mode,
        })
    }

    fn resize(&mut self, new_size: PhysicalSize<u32>) {
        self.size = clamp_size(new_size);
        self.config.width = self.size.width;
        self.config.height = self.size.height;
        self.surface.configure(&self.device, &self.config);
        self.update_vertices();
    }

    fn upload_frame(&mut self, frame: FrameMessage) {
        let texture_format = match frame.pixel_format {
            PixelFormat::Rgba8 => wgpu::TextureFormat::Rgba8UnormSrgb,
            PixelFormat::Bgra8 => wgpu::TextureFormat::Bgra8UnormSrgb,
        };
        let recreate = self.frame.as_ref().is_none_or(|current| {
            current.width != frame.width
                || current.height != frame.height
                || current.format != texture_format
        });

        if recreate {
            self.frame = Some(self.create_gpu_frame(frame.width, frame.height, texture_format));
        }

        if let Some(current) = &self.frame {
            self.queue.write_texture(
                wgpu::ImageCopyTexture {
                    texture: &current.texture,
                    mip_level: 0,
                    origin: wgpu::Origin3d::ZERO,
                    aspect: wgpu::TextureAspect::All,
                },
                &frame.data,
                wgpu::ImageDataLayout {
                    offset: 0,
                    bytes_per_row: Some(frame.width * 4),
                    rows_per_image: Some(frame.height),
                },
                wgpu::Extent3d {
                    width: frame.width,
                    height: frame.height,
                    depth_or_array_layers: 1,
                },
            );
        }

        self.active_fit_mode = if frame.fit_mode == FitMode::Default {
            self.default_fit_mode
        } else {
            frame.fit_mode
        };
        self.update_vertices();
    }

    fn render(&mut self) -> Result<(), wgpu::SurfaceError> {
        let output = self.surface.get_current_texture()?;
        let view = output
            .texture
            .create_view(&wgpu::TextureViewDescriptor::default());
        let mut encoder = self
            .device
            .create_command_encoder(&wgpu::CommandEncoderDescriptor {
                label: Some("frame render encoder"),
            });

        {
            let mut render_pass = encoder.begin_render_pass(&wgpu::RenderPassDescriptor {
                label: Some("frame render pass"),
                color_attachments: &[Some(wgpu::RenderPassColorAttachment {
                    view: &view,
                    resolve_target: None,
                    ops: wgpu::Operations {
                        load: wgpu::LoadOp::Clear(wgpu::Color::BLACK),
                        store: wgpu::StoreOp::Store,
                    },
                })],
                depth_stencil_attachment: None,
                timestamp_writes: None,
                occlusion_query_set: None,
            });

            if let Some(frame) = &self.frame {
                render_pass.set_pipeline(&self.pipeline);
                render_pass.set_bind_group(0, &frame.bind_group, &[]);
                render_pass.set_vertex_buffer(0, self.vertex_buffer.slice(..));
                render_pass.draw(0..6, 0..1);
            }
        }

        self.queue.submit(Some(encoder.finish()));
        output.present();
        Ok(())
    }

    fn create_gpu_frame(&self, width: u32, height: u32, format: wgpu::TextureFormat) -> GpuFrame {
        let texture = self.device.create_texture(&wgpu::TextureDescriptor {
            label: Some("submitted frame texture"),
            size: wgpu::Extent3d {
                width,
                height,
                depth_or_array_layers: 1,
            },
            mip_level_count: 1,
            sample_count: 1,
            dimension: wgpu::TextureDimension::D2,
            format,
            usage: wgpu::TextureUsages::TEXTURE_BINDING | wgpu::TextureUsages::COPY_DST,
            view_formats: &[],
        });
        let view = texture.create_view(&wgpu::TextureViewDescriptor::default());
        let bind_group = self.device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: Some("submitted frame bind group"),
            layout: &self.texture_bind_group_layout,
            entries: &[
                wgpu::BindGroupEntry {
                    binding: 0,
                    resource: wgpu::BindingResource::TextureView(&view),
                },
                wgpu::BindGroupEntry {
                    binding: 1,
                    resource: wgpu::BindingResource::Sampler(&self.sampler),
                },
            ],
        });
        GpuFrame {
            width,
            height,
            format,
            texture,
            _view: view,
            bind_group,
        }
    }

    fn update_vertices(&self) {
        let vertices = if let Some(frame) = &self.frame {
            frame_vertices(
                frame.width,
                frame.height,
                self.size.width,
                self.size.height,
                self.active_fit_mode,
            )
        } else {
            empty_vertices()
        };
        self.queue
            .write_buffer(&self.vertex_buffer, 0, bytemuck::cast_slice(&vertices));
    }
}

struct GpuFrame {
    width: u32,
    height: u32,
    format: wgpu::TextureFormat,
    texture: wgpu::Texture,
    _view: wgpu::TextureView,
    bind_group: wgpu::BindGroup,
}

#[repr(C)]
#[derive(Clone, Copy, Pod, Zeroable)]
struct Vertex {
    position: [f32; 2],
    tex_coords: [f32; 2],
}

impl Vertex {
    fn layout<'a>() -> wgpu::VertexBufferLayout<'a> {
        const ATTRIBUTES: [wgpu::VertexAttribute; 2] =
            wgpu::vertex_attr_array![0 => Float32x2, 1 => Float32x2];
        wgpu::VertexBufferLayout {
            array_stride: std::mem::size_of::<Vertex>() as wgpu::BufferAddress,
            step_mode: wgpu::VertexStepMode::Vertex,
            attributes: &ATTRIBUTES,
        }
    }
}

fn frame_vertices(
    source_width: u32,
    source_height: u32,
    target_width: u32,
    target_height: u32,
    fit_mode: FitMode,
) -> [Vertex; 6] {
    let (draw_width, draw_height) = match fit_mode {
        FitMode::Stretch | FitMode::Default => (target_width as f32, target_height as f32),
        FitMode::Native => (source_width as f32, source_height as f32),
        FitMode::Contain => {
            let scale = (target_width as f32 / source_width as f32)
                .min(target_height as f32 / source_height as f32);
            (source_width as f32 * scale, source_height as f32 * scale)
        }
        FitMode::Cover => {
            let scale = (target_width as f32 / source_width as f32)
                .max(target_height as f32 / source_height as f32);
            (source_width as f32 * scale, source_height as f32 * scale)
        }
    };
    let x = (target_width as f32 - draw_width) * 0.5;
    let y = (target_height as f32 - draw_height) * 0.5;

    let left = x / target_width as f32 * 2.0 - 1.0;
    let right = (x + draw_width) / target_width as f32 * 2.0 - 1.0;
    let top = 1.0 - y / target_height as f32 * 2.0;
    let bottom = 1.0 - (y + draw_height) / target_height as f32 * 2.0;

    [
        Vertex {
            position: [left, top],
            tex_coords: [0.0, 0.0],
        },
        Vertex {
            position: [left, bottom],
            tex_coords: [0.0, 1.0],
        },
        Vertex {
            position: [right, bottom],
            tex_coords: [1.0, 1.0],
        },
        Vertex {
            position: [left, top],
            tex_coords: [0.0, 0.0],
        },
        Vertex {
            position: [right, bottom],
            tex_coords: [1.0, 1.0],
        },
        Vertex {
            position: [right, top],
            tex_coords: [1.0, 0.0],
        },
    ]
}

fn empty_vertices() -> [Vertex; 6] {
    [Vertex {
        position: [0.0, 0.0],
        tex_coords: [0.0, 0.0],
    }; 6]
}

fn clamp_size(size: PhysicalSize<u32>) -> PhysicalSize<u32> {
    PhysicalSize::new(size.width.max(1), size.height.max(1))
}
