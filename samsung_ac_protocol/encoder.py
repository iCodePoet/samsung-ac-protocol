from typing import List
from .models import SamsungACRequest

def _count_bits(v: int) -> int:
    return bin(v).count('1')

def _calculate_checksum(raw: List[int]) -> None:
    # Section 1
    sum1 = 255 - (_count_bits(raw[0]) + _count_bits(raw[1] & 0x0F) + _count_bits(raw[2] & 0xF0) + 
                  _count_bits(raw[3]) + _count_bits(raw[4]) + _count_bits(raw[5]) + _count_bits(raw[6]))
    raw[1] = (raw[1] & 0x0F) | ((sum1 & 0xF) << 4)
    raw[2] = (raw[2] & 0xF0) | ((sum1 >> 4) & 0xF)
    
    # Section 2
    sum2 = 255 - (_count_bits(raw[7]) + _count_bits(raw[8] & 0x0F) + _count_bits(raw[9] & 0xF0) + 
                  _count_bits(raw[10]) + _count_bits(raw[11]) + _count_bits(raw[12]) + _count_bits(raw[13]))
    raw[8] = (raw[8] & 0x0F) | ((sum2 & 0xF) << 4)
    raw[9] = (raw[9] & 0xF0) | ((sum2 >> 4) & 0xF)
    
    # Section 3
    sum3 = 255 - (_count_bits(raw[14]) + _count_bits(raw[15] & 0x0F) + _count_bits(raw[16] & 0xF0) + 
                  _count_bits(raw[17]) + _count_bits(raw[18]) + _count_bits(raw[19]) + _count_bits(raw[20]))
    raw[15] = (raw[15] & 0x0F) | ((sum3 & 0xF) << 4)
    raw[16] = (raw[16] & 0xF0) | ((sum3 >> 4) & 0xF)


def encode(request: SamsungACRequest) -> List[int]:
    """
    Encodes the desired AC state into a 21-byte Samsung IR payload.
    
    Args:
        request (SamsungACRequest): The desired state to encode.
        
    Returns:
        List[int]: A 21-byte array representing the IR payload.
    """
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
