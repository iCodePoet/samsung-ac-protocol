import pytest
from samsung_ac_decoder import decode_samsung_timers

def test_decode_short_payload():
    """Test that a payload with fewer than 21 bytes returns None."""
    assert decode_samsung_timers([0x00] * 20) is None

def test_no_timers():
    """Test that a payload with no timers returns 0.0 for both."""
    payload = [0x00] * 21
    timers = decode_samsung_timers(payload)
    assert timers is not None
    assert timers["off_hours"] == 0.0
    assert timers["on_hours"] == 0.0

def test_off_timer_only_1_hour():
    """Test setting only the Off timer to 1.0 hour (val = 8 = 0x08).
    Off timer is in B9_upper and B10_lower.
    So B9 = 0x80, B10 = 0x00
    """
    payload = [0x00] * 21
    payload[9] = 0x80
    payload[10] = 0x00
    timers = decode_samsung_timers(payload)
    
    assert timers is not None
    assert timers["off_hours"] == 1.0
    assert timers["on_hours"] == 0.0

def test_on_timer_only_half_hour():
    """Test setting only the On timer to 0.5 hours (val = 3 = 0x03).
    On timer is in B10_upper and B11_lower.
    So B10 = 0x30, B11 = 0x00
    """
    payload = [0x00] * 21
    payload[10] = 0x30
    payload[11] = 0x00
    timers = decode_samsung_timers(payload)
    
    assert timers is not None
    assert timers["off_hours"] == 0.0
    assert timers["on_hours"] == 0.5

def test_dual_timer():
    """Test setting both On (0.5h, val=3) and Off (1.0h, val=8) timers.
    Off timer (8): B9_upper = 8, B10_lower = 0
    On timer (3): B10_upper = 3, B11_lower = 0
    Resulting bytes:
    B9 = 0x80
    B10 = 0x30
    B11 = 0x00
    """
    payload = [0x00] * 21
    payload[9] = 0x80
    payload[10] = 0x30
    payload[11] = 0x00
    timers = decode_samsung_timers(payload)
    
    assert timers is not None
    assert timers["off_hours"] == 1.0
    assert timers["on_hours"] == 0.5

def test_complex_dual_timer():
    """Test a more complex real-world dual timer:
    Off: 2.5h (val = 2*8+3 = 19 = 0x13) => B9_upper=3, B10_lower=1 => wait, val is 12-bit?
    Let's check the hex math for 0x13: 1 is upper nibble, 3 is lower nibble.
    Wait, B9_upper + B10_lower.
    off_val = ((B10 & 0x0F) << 4) + (B9 >> 4)
    If off_val = 0x13, then (B10 & 0x0F) = 1, (B9 >> 4) = 3
    So B10_lower = 1, B9_upper = 3
    B9 = 0x30, B10 = 0x01
    
    On: 12.0h (val = 12*8 = 96 = 0x60)
    on_val = ((B11 & 0x0F) << 4) + (B10 >> 4)
    If on_val = 0x60, then (B11 & 0x0F) = 6, (B10 >> 4) = 0
    So B11_lower = 6, B10_upper = 0
    
    Combining B10: B10_upper=0, B10_lower=1 => B10 = 0x01
    So B9 = 0x30, B10 = 0x01, B11 = 0x06
    """
    payload = [0x00] * 21
    payload[9] = 0x30
    payload[10] = 0x01
    payload[11] = 0x06
    timers = decode_samsung_timers(payload)
    
    assert timers is not None
    assert timers["off_hours"] == 2.5
    assert timers["on_hours"] == 12.0
