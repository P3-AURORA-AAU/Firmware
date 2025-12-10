const std = @import("std");

const c = @cImport({
    @cInclude("termios.h");
    @cInclude("unistd.h");
    @cInclude("fcntl.h");
    @cInclude("poll.h");
    @cInclude("errno.h");
});

const UARTError = error{
    Timeout,
    UnexpectedResponse,
    IoError,
};

const syn: u8 = 0x53;
const synAck: u8 = 0x54;
const ack: u8 = 0x55;

pub fn main() !void {
    const uart_path = "/dev/ttyAMA0";

    const fd = c.open(uart_path, c.O_RDWR | c.O_NOCTTY | c.O_SYNC, @as(c.mode_t, 0o666));
    defer _ = c.close(fd);

    var tio: c.struct_termios = undefined;
    if (c.tcgetattr(fd, &tio) != 0) {
        return UARTError.IoError;
    }

    const baudRate: c.speed_t = c.B9600; // using C macro
    if (c.cfsetispeed(&tio, baudRate) != 0) {
        return UARTError.IoError;
    }
    if (c.cfsetospeed(&tio, baudRate) != 0) {
        return UARTError.IoError;
    }

    // Configure raw 8-N-1
    tio.c_iflag = 0;
    tio.c_oflag = 0;
    tio.c_lflag = 0;
    tio.c_cflag = c.CS8 | c.CREAD | c.CLOCAL;

    if (c.tcsetattr(fd, c.TCSANOW, &tio) != 0) {
        return UARTError.IoError;
    }

    const ok = handshake(fd, 2_000_000) catch |err| {
        std.debug.print("Handshake failed: {s}\n", .{@errorName(err)});
        return;
    };
    if (ok) {
        std.debug.print("Handshake successful!\n", .{});
    } else {
        std.debug.print("Handshake failed.\n", .{});
    }
}

fn writeByte(fd: c_int, b: u8) UARTError!void {
    const buf: [1]u8 = .{b};
    const n = c.write(fd, &buf, 1);
    if (n < 0) {
        return UARTError.IoError;
    }
    if (n != 1) {
        return UARTError.IoError;
    }
}

fn readByte(fd: c_int, timeout_us: i32) UARTError!u8 {
    var pfd: c.struct_pollfd = .{
        .fd = fd,
        .events = c.POLLIN,
        .revents = 0,
    };
    const nready = c.poll(&pfd, 1, @divFloor(timeout_us, 1000));
    if (nready < 0) {
        return UARTError.IoError;
    }
    if (nready == 0) {
        return UARTError.Timeout;
    }
    var buf: [1]u8 = undefined;
    const n = c.read(fd, &buf, 1);
    if (n < 0) {
        return UARTError.IoError;
    }
    if (n != 1) {
        return UARTError.IoError;
    }
    return buf[0];
}

fn handshake(fd: c_int, timeout_us: i32) UARTError!bool {
    std.debug.print("Starting handshake", .{});
    try writeByte(fd, syn);

    const resp = try readByte(fd, timeout_us);
    if (resp != synAck) {
        return UARTError.UnexpectedResponse;
    }

    try writeByte(fd, ack);
    return true;
}
