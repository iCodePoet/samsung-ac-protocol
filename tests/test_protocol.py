import pytest
from samsung_ac_protocol import _decode_timers, decode, encode, SamsungACRequest

def test_decode_short_payload():
    assert _decode_timers([0x00] * 20) is None

def test_encode_and_decode_loop():
    """Test that we can encode a state and immediately decode it perfectly."""
    req = SamsungACRequest(power=True, mode=1, temp=24, fan=4)
    raw = encode(req) # Cool, 24C, Med fan
    
    assert len(raw) == 21
    
    state = decode(raw)
    assert state is not None
    assert state.power is True
    assert state.mode == 1
    assert state.temp == 24
    assert state.fan == 4
    assert state.timers.on_hours == 0.0
    assert state.timers.off_hours == 0.0

def test_encode_timers():
    """Test encoding timers and verifying with the decoder."""
    # Test Off Timer (2 hours = 8 * 15m)
    req = SamsungACRequest(power=True, mode=1, temp=24, fan=4, timer_mode=2, timer_15m=8)
    raw = encode(req)
    state = decode(raw)
    assert state.timers.off_hours == 2.0
    assert state.timers.on_hours == 0.0
    
    # Test On Timer (1.5 hours = 6 * 15m)
    req2 = SamsungACRequest(power=False, mode=0, temp=25, fan=0, timer_mode=1, timer_15m=6)
    raw = encode(req2)
    state = decode(raw)
    assert state.timers.on_hours == 1.5
    assert state.timers.off_hours == 0.0
