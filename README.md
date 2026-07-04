# Samsung AC IR Protocol 🕵️‍♂️❄️

A Python package for encoding and decoding Samsung Air Conditioner IR remote payloads, featuring reverse-engineered checksum handling and timer decoding for Samsung's compact On/Off timer representation.

## Disclaimer / Limitations
⚠️ **Note:** This protocol was entirely reverse-engineered through observation. While it has been tested on the models listed below, **there is no guarantee that it works perfectly or reliably even for those specific devices**, let alone other Samsung AC models or edge cases. There may be additional hidden flags or behaviors in other bytes that we have yet to discover. Use this library strictly at your own risk and feel free to contribute if you find discrepancies!


## The Mystery
While standard Samsung AC IR protocols (Power, Temp, Mode, Fan) are well documented in open-source projects like [HeatpumpIR](https://github.com/ToniA/arduino-heatpumpir), the **timer scheduling functionality** has remained a black box. 

When observing the raw IR hex bytes sent by a Samsung remote while setting both "On Timers" and "Off Timers", the data did not simply represent 15-minute intervals. Furthermore, setting an Off Timer unexpectedly changed bytes associated with the On Timer. 

Through raw byte analysis, we discovered that Samsung employs a compact bit-shifting and packing algorithm to fit timer durations into just 2.5 bytes of data.

---

## The Protocol (21 Bytes Total)

Samsung AC IR payloads consist of 21 bytes (3 sections of 7 bytes). 
The timer data is heavily compressed into **Section 2**, specifically across **Byte 9, Byte 10, and Byte 11**.

### 🧩 The Tetris Packing
Because a timer can range from 0.5 hours to 24.0 hours, it requires more than 4 bits to store. Samsung chose to split these bits across byte boundaries:

- **Off-Timer**: Stored in the **Upper Nibble of Byte 9** and the **Lower Nibble of Byte 10**.
- **On-Timer**: Stored in the **Upper Nibble of Byte 10** and the **Lower Nibble of Byte 11**.

> **Note:** `Byte 12` often acts as a deceptive cache holding old timer data. When fully decoding dual-timers, `Byte 12` must be ignored in favor of the tightly packed B9~B11 region.

### 🔢 The Cryptic Formula (`val = H * 8 + 3`)
Even after successfully unpacking the nibbles into an integer `val`, the resulting integer is not a simple representation of hours or minutes. Samsung uses the following mathematical formula to encode the time:

- If the time is a **whole hour** (e.g., 1.0, 2.0, 3.0): `val = Hour * 8`
- If the time is a **half hour** (e.g., 0.5, 1.5, 2.5): `val = Hour * 8 + 3`

#### Examples:
| Actual Time | Formula Applied | Binary `val` (Packed) |
|-------------|-----------------|-----------------------|
| 0.5 hours   | `0 * 8 + 3 = 3` | `0000 0011`           |
| 1.0 hours   | `1 * 8 = 8`     | `0000 1000`           |
| 1.5 hours   | `1 * 8 + 3 = 11`| `0000 1011`           |
| 2.0 hours   | `2 * 8 = 16`    | `0001 0000`           |

---

## 🚀 Installation

You can install the package directly from PyPI:

```bash
pip install samsung-ac-protocol
```
Or if you're using `uv`:
```bash
uv pip install samsung-ac-protocol
```

---

## 🛠 Usage (Python Codec)

Using the `samsung-ac-protocol` package is extremely simple.

### Decoding (IR Sniffing)
Pass the 21-byte raw IR payload to the `decode()` function, and it will parse all the state information.

```python
from samsung_ac_protocol import decode

# Example: 21-byte raw IR payload captured from an AC remote
raw_payload = [
    0x02, 0x92, 0x0F, 0x00, 0x00, 0x00, 0xF0, 0x01, 
    0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 
    0x00, 0x00, 0x00, 0x00, 0x00
]

state = decode(raw_payload)
print(state)
```

If you want the decoder to reject corrupted captures, enable checksum validation:

```python
state = decode(raw_payload, validate_checksum=True)
```

You can also decode the timer fields directly:

```python
from samsung_ac_protocol import decode_timers

timers = decode_timers(raw_payload)
```

### Encoding & Timings (IR Blasting)
You can encode a desired state back into a 21-byte payload, and optionally convert it to raw microsecond timings to send directly to an IR LED. The encoder validates mode, temperature, fan, and timer ranges before generating bytes.

```python
from samsung_ac_protocol import encode, to_timings, SamsungACRequest

req = SamsungACRequest(
    power=True, 
    mode=1,   # 1 = Cool
    temp=24,  # 24C
    fan=4,    # 4 = Medium
    timer_mode=2, # 2 = Off Timer
    timer_15m=8   # 2 hours
)

# 1. Generate 21-byte hex payload
payload_bytes = encode(req)

# 2. Generate 347 timing pulses for IR transmission
timings = to_timings(payload_bytes)
```

Supported encoder ranges:

- `mode`: `0` Auto, `1` Cool, `2` Dry, `3` Fan, `4` Heat
- `temp`: `16` through `30`
- `fan`: `0` Auto, `2` Low, `4` Medium, `5` High
- `timer_mode`: `0` None, `1` On Timer, `2` Off Timer, `3` fixed special timer mode
- `timer_15m`: `0` through `96`, representing 15-minute units up to 24 hours. On/Off timers require a value greater than `0`; `timer_mode=3` accepts only `0` or `4`.


## Verified Devices

This reverse engineering was tested and verified to work on the following hardware:
- **Samsung WindFree™ 1-Way Cassette** 
  - Model Numbers: `AC009BN1DCH` (9K Btu), `AC012BN1DCH` (12K Btu), `AC018BN1DCH` (18K Btu)

## Contribution
Discovered while building a custom local IR bridge for Hermes Agent. Feel free to use this algorithm to implement full dual-timer support in your own open-source IR libraries!



## License
This project is licensed under the [MIT License](LICENSE).
You are free to use, modify, and distribute this software, but it is provided "AS IS" with absolutely no liability or warranty.
