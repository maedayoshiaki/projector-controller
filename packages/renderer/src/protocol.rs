use std::io::{self, Read};

pub const HEADER_LEN: usize = 20;
const FRAME_MAGIC: &[u8; 4] = b"PCF1";
const QUIT_MAGIC: &[u8; 4] = b"PCQ1";
const MAX_FRAME_BYTES: u32 = 512 * 1024 * 1024;

#[derive(Debug)]
pub enum ProtocolMessage {
    Frame(FrameMessage),
    Shutdown,
}

#[derive(Clone, Debug)]
pub struct FrameMessage {
    pub width: u32,
    pub height: u32,
    pub pixel_format: PixelFormat,
    pub fit_mode: FitMode,
    pub data: Vec<u8>,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum PixelFormat {
    Rgba8,
    Bgra8,
}

impl PixelFormat {
    pub fn from_wire(value: u8) -> io::Result<Self> {
        match value {
            1 => Ok(Self::Rgba8),
            2 => Ok(Self::Bgra8),
            _ => Err(invalid_data(format!("unsupported pixel format: {value}"))),
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum FitMode {
    Default,
    Contain,
    Cover,
    Stretch,
    Native,
}

impl FitMode {
    pub fn from_wire(value: u8) -> io::Result<Self> {
        match value {
            0 => Ok(Self::Default),
            1 => Ok(Self::Contain),
            2 => Ok(Self::Cover),
            3 => Ok(Self::Stretch),
            4 => Ok(Self::Native),
            _ => Err(invalid_data(format!("unsupported fit mode: {value}"))),
        }
    }
}

pub fn read_message(reader: &mut impl Read) -> io::Result<Option<ProtocolMessage>> {
    let mut header = [0_u8; HEADER_LEN];
    match reader.read_exact(&mut header) {
        Ok(()) => {}
        Err(error) if error.kind() == io::ErrorKind::UnexpectedEof => return Ok(None),
        Err(error) => return Err(error),
    }

    let magic = &header[0..4];
    if magic == QUIT_MAGIC {
        return Ok(Some(ProtocolMessage::Shutdown));
    }
    if magic != FRAME_MAGIC {
        return Err(invalid_data("invalid frame header magic"));
    }

    let width = read_u32(&header[4..8]);
    let height = read_u32(&header[8..12]);
    let pixel_format = PixelFormat::from_wire(header[12])?;
    let fit_mode = FitMode::from_wire(header[13])?;
    let byte_len = read_u32(&header[16..20]);

    if width == 0 || height == 0 {
        return Err(invalid_data("frame width and height must be positive"));
    }

    let expected = width
        .checked_mul(height)
        .and_then(|pixels| pixels.checked_mul(4))
        .ok_or_else(|| invalid_data("frame dimensions overflow"))?;
    if byte_len != expected {
        return Err(invalid_data(format!(
            "frame byte length mismatch: got {byte_len}, expected {expected}"
        )));
    }
    if byte_len > MAX_FRAME_BYTES {
        return Err(invalid_data(format!(
            "frame is too large: {byte_len} bytes"
        )));
    }

    let mut data = vec![0_u8; byte_len as usize];
    reader.read_exact(&mut data)?;
    Ok(Some(ProtocolMessage::Frame(FrameMessage {
        width,
        height,
        pixel_format,
        fit_mode,
        data,
    })))
}

fn read_u32(bytes: &[u8]) -> u32 {
    u32::from_le_bytes(bytes.try_into().expect("slice length checked by caller"))
}

fn invalid_data(message: impl Into<String>) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidData, message.into())
}

#[cfg(test)]
mod tests {
    use std::io::Cursor;

    use super::{read_message, FitMode, PixelFormat, ProtocolMessage};

    #[test]
    fn reads_frame_message() {
        let mut bytes = Vec::new();
        bytes.extend_from_slice(b"PCF1");
        bytes.extend_from_slice(&2_u32.to_le_bytes());
        bytes.extend_from_slice(&1_u32.to_le_bytes());
        bytes.push(1);
        bytes.push(2);
        bytes.extend_from_slice(&0_u16.to_le_bytes());
        bytes.extend_from_slice(&8_u32.to_le_bytes());
        bytes.extend_from_slice(&[1, 2, 3, 4, 5, 6, 7, 8]);

        let message = read_message(&mut Cursor::new(bytes)).expect("valid frame");
        match message {
            Some(ProtocolMessage::Frame(frame)) => {
                assert_eq!(frame.width, 2);
                assert_eq!(frame.height, 1);
                assert_eq!(frame.pixel_format, PixelFormat::Rgba8);
                assert_eq!(frame.fit_mode, FitMode::Cover);
                assert_eq!(frame.data, vec![1, 2, 3, 4, 5, 6, 7, 8]);
            }
            _ => panic!("expected frame message"),
        }
    }

    #[test]
    fn reads_shutdown_message() {
        let mut bytes = Vec::new();
        bytes.extend_from_slice(b"PCQ1");
        bytes.extend_from_slice(&[0; 16]);

        let message = read_message(&mut Cursor::new(bytes)).expect("valid quit");
        assert!(matches!(message, Some(ProtocolMessage::Shutdown)));
    }
}
