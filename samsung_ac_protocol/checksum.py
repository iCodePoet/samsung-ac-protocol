from typing import List


def count_bits(value: int) -> int:
    return bin(value).count("1")


def apply_checksum(raw: List[int]) -> None:
    for offset in range(0, len(raw), 7):
        section = raw[offset:offset + 7]
        if len(section) != 7:
            raise ValueError("Payload sections must be exactly 7 bytes.")

        checksum = 255 - (
            count_bits(raw[offset])
            + count_bits(raw[offset + 1] & 0x0F)
            + count_bits(raw[offset + 2] & 0xF0)
            + count_bits(raw[offset + 3])
            + count_bits(raw[offset + 4])
            + count_bits(raw[offset + 5])
            + count_bits(raw[offset + 6])
        )
        raw[offset + 1] = (raw[offset + 1] & 0x0F) | ((checksum & 0xF) << 4)
        raw[offset + 2] = (raw[offset + 2] & 0xF0) | ((checksum >> 4) & 0xF)


def validate_bytes(bytes_arr: List[int]) -> None:
    for value in bytes_arr:
        if not isinstance(value, int) or value < 0 or value > 0xFF:
            raise ValueError("Payload byte values must be integers between 0 and 255.")


def has_valid_checksum(bytes_arr: List[int]) -> bool:
    if len(bytes_arr) % 7 != 0:
        return False

    expected = list(bytes_arr)
    apply_checksum(expected)
    return expected == bytes_arr
