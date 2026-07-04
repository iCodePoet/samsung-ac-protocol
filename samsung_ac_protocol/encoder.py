from typing import List
from .models import SamsungACRequest
from .checksum import apply_checksum


def _calculate_checksum(raw: List[int]) -> None:
    apply_checksum(raw)


def _validate_request(request: SamsungACRequest) -> None:
    if request.mode not in {0, 1, 2, 3, 4}:
        raise ValueError("mode must be one of 0, 1, 2, 3, or 4.")
    if not 16 <= request.temp <= 30:
        raise ValueError("temp must be between 16 and 30 Celsius.")
    if request.fan not in {0, 2, 4, 5}:
        raise ValueError("fan must be one of 0, 2, 4, or 5.")
    if request.timer_mode not in {0, 1, 2, 3}:
        raise ValueError("timer_mode must be one of 0, 1, 2, or 3.")
    if not 0 <= request.timer_15m <= 96:
        raise ValueError("timer_15m must be between 0 and 96.")
    if request.timer_mode == 0 and request.timer_15m != 0:
        raise ValueError("timer_15m must be 0 when timer_mode is 0.")
    if request.timer_mode in {1, 2} and request.timer_15m == 0:
        raise ValueError("timer_15m must be greater than 0 for on/off timers.")
    if request.timer_mode == 3 and request.timer_15m not in {0, 4}:
        raise ValueError("timer_15m must be 0 or 4 for timer_mode 3.")


def encode(request: SamsungACRequest) -> List[int]:
    """
    Encodes the desired AC state into a 21-byte Samsung IR payload.
    
    Args:
        request (SamsungACRequest): The desired state to encode.
        
    Returns:
        List[int]: A 21-byte array representing the IR payload.
    """
    _validate_request(request)

    raw = [
        0x02, 0x92, 0x0F, 0x00, 0x00, 0x00, 0xF0,
        0x01, 0xD2, 0x0F, 0x00, 0x00, 0x00, 0x00,
        0x01, 0xC2, 0xFE, 0x71, 0x80, 0x35, 0xF0
    ]
    
    if request.power:
        raw[6] = 0xF0
        raw[20] = 0xF0
    else:
        raw[6] = 0xC0
        raw[20] = 0xC0
        
    t = 8 if request.mode == 3 else (request.temp - 16)
    raw[18] = (raw[18] & 0x0F) | (t << 4)
    
    raw[19] = 1 | (request.fan << 1) | (request.mode << 4)
    
    if request.timer_mode == 1:
        raw[8] = 0xA2
        raw[9] = 0x0F
        raw[10] = 0x30
        raw[11] = 0x00
        raw[12] = request.timer_15m
    elif request.timer_mode == 2:
        raw[8] = 0xB2
        raw[9] = 0x8F
        raw[10] = 0x00
        raw[11] = 0x00
        raw[12] = request.timer_15m
    elif request.timer_mode == 3:
        raw[8] = 0x92
        raw[9] = 0xBF
        raw[10] = 0x00
        raw[11] = 0x00
        raw[12] = 0x04
        
    _calculate_checksum(raw)
    return raw


def to_timings(bytes_arr: List[int]) -> List[int]:
    """
    Converts a 21-byte Samsung IR payload into raw microsecond pulse timings.
    
    Args:
        bytes_arr (List[int]): A 21-byte array representing the IR payload.
        
    Returns:
        List[int]: An array of 347 integers representing pulse and space durations in microseconds.
    """
    if len(bytes_arr) != 21:
        raise ValueError("Payload must be exactly 21 bytes.")
        
    timings = []
    
    for section in range(3):
        if section > 0:
            timings.append(500)
            timings.append(3000)
            
        timings.append(3000)
        timings.append(9000)
        
        for i in range(7):
            b = bytes_arr[section * 7 + i]
            for bit in range(8):
                timings.append(500)
                if (b >> bit) & 1:
                    timings.append(1500)
                else:
                    timings.append(500)
                    
    timings.append(500)
    return timings
