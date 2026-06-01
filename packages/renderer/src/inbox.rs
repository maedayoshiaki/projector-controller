use std::collections::VecDeque;
use std::sync::{Condvar, Mutex};

use crate::protocol::FrameMessage;

/// How the renderer copes when frames arrive faster than it can present them.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Backpressure {
    /// Keep only the newest unrendered frame, dropping older ones. The producer never
    /// blocks, so projected output stays fresh and latency never accumulates. Default.
    Latest,
    /// Render every frame: block the IPC reader when the buffer is full, which stops
    /// draining the socket and back-pressures the producer over TCP. Use this to play
    /// every frame of a paced source (e.g. video) without dropping any.
    All,
}

/// A bounded hand-off between the IPC reader thread and the render loop.
///
/// A single structure expresses both policies, which is why it also solves the old
/// unbounded-queue growth: `Latest` is a one-slot overwrite, `All` is a tiny FIFO that
/// blocks the producer instead of buffering without limit.
pub struct FrameInbox {
    mode: Backpressure,
    capacity: usize,
    queue: Mutex<VecDeque<FrameMessage>>,
    space: Condvar,
}

impl FrameInbox {
    pub fn new(mode: Backpressure) -> Self {
        // Latest needs a single slot. All keeps a couple so decode/transfer can overlap
        // one frame of rendering, but stays small so a runaway producer is paced quickly.
        let capacity = match mode {
            Backpressure::Latest => 1,
            Backpressure::All => 3,
        };
        Self {
            mode,
            capacity,
            queue: Mutex::new(VecDeque::with_capacity(capacity)),
            space: Condvar::new(),
        }
    }

    /// Called by the IPC reader thread. In `Latest` mode this overwrites any pending
    /// frame (dropping it); in `All` mode this blocks until there is room.
    pub fn push(&self, frame: FrameMessage) {
        let mut queue = self.queue.lock().expect("frame inbox poisoned");
        match self.mode {
            Backpressure::Latest => {
                queue.clear();
                queue.push_back(frame);
            }
            Backpressure::All => {
                while queue.len() >= self.capacity {
                    queue = self.space.wait(queue).expect("frame inbox poisoned");
                }
                queue.push_back(frame);
            }
        }
    }

    /// Called by the render loop when woken. Returns the next frame to render, if any,
    /// and frees a slot so a blocked producer (`All` mode) can proceed.
    pub fn pop(&self) -> Option<FrameMessage> {
        let mut queue = self.queue.lock().expect("frame inbox poisoned");
        let frame = queue.pop_front();
        if frame.is_some() {
            self.space.notify_one();
        }
        frame
    }
}

#[cfg(test)]
mod tests {
    use super::{Backpressure, FrameInbox};
    use crate::protocol::{FitMode, FrameMessage, PixelFormat};

    fn frame(tag: u8) -> FrameMessage {
        FrameMessage {
            width: 1,
            height: 1,
            pixel_format: PixelFormat::Rgba8,
            fit_mode: FitMode::Default,
            data: vec![tag, tag, tag, tag],
        }
    }

    #[test]
    fn latest_mode_keeps_only_newest() {
        let inbox = FrameInbox::new(Backpressure::Latest);
        inbox.push(frame(1));
        inbox.push(frame(2));
        inbox.push(frame(3));
        assert_eq!(inbox.pop().expect("a frame").data, vec![3, 3, 3, 3]);
        assert!(inbox.pop().is_none());
    }

    #[test]
    fn all_mode_preserves_order() {
        let inbox = FrameInbox::new(Backpressure::All);
        inbox.push(frame(1));
        inbox.push(frame(2));
        assert_eq!(inbox.pop().expect("a frame").data, vec![1, 1, 1, 1]);
        assert_eq!(inbox.pop().expect("a frame").data, vec![2, 2, 2, 2]);
        assert!(inbox.pop().is_none());
    }
}
