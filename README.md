# Samsung AC IR Decoder 🕵️‍♂️❄️

A Python package for decoding Samsung Air Conditioner IR remote payloads, featuring a complete reverse-engineered algorithm for their obscure dual-timer (On/Off) binary compression.

## Disclaimer / Limitations
⚠️ **Note:** This protocol was entirely reverse-engineered through observation. While it has been tested on the models listed below, **there is no guarantee that it works perfectly or reliably even for those specific devices**, let alone other Samsung AC models or edge cases. There may be additional hidden flags or behaviors in other bytes that we have yet to discover. Use this library strictly at your own risk and feel free to contribute if you find discrepancies!


## The Mystery
While standard Samsung AC IR protocols (Power, Temp, Mode, Fan) are well documented in open-source projects like [HeatpumpIR](https://github.com/ToniA/arduino-heatpumpir), the **timer scheduling functionality** has remained a black box. 

When observing the raw IR hex bytes sent by a Samsung remote while setting both "On Timers" and "Off Timers", the data did not simply represent 15-minute intervals. Furthermore, setting an Off Timer unexpectedly changed bytes associated with the On Timer. 

Through meticulous raw byte analysis, we discovered that Samsung employs a highly compact bit-shifting and packing algorithm to fit **two independent timer durations (On and Off) spanning up to 24 hours into just 2.5 bytes of data!**

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

## 🛠 Python Decoder Implementation

Here is the Python algorithm to flawlessly extract both On-Timers and Off-Timers from a raw 21-byte Samsung IR payload array:

```python
def decode_samsung_timers(bytes_arr):
    if len(bytes_arr) < 21:
        return

    # 1. Extract Off-Timer (Byte 10 Lower + Byte 9 Upper)
    off_val = ((bytes_arr[10] & 0x0F) << 4) + (bytes_arr[9] >> 4)
    off_hours = 0.0
    
    if off_val > 0:
        off_hours = (off_val // 8) + (0.5 if off_val % 8 == 3 else 0.0)

    # 2. Extract On-Timer (Byte 11 Lower + Byte 10 Upper)
    on_val = ((bytes_arr[11] & 0x0F) << 4) + (bytes_arr[10] >> 4)
    on_hours = 0.0
    
    if on_val > 0:
        on_hours = (on_val // 8) + (0.5 if on_val % 8 == 3 else 0.0)

    # 3. Print Results
    if off_hours > 0 and on_hours > 0:
        print(f"Dual Timer Active: On in {on_hours:.1f}h, Off in {off_hours:.1f}h")
    elif off_hours > 0:
        print(f"Off Timer Active: Off in {off_hours:.1f}h")
    elif on_hours > 0:
        print(f"On Timer Active: On in {on_hours:.1f}h")
    else:
        print("No Active Timers.")

# Example Payload: On Timer 0.5h, Off Timer 1.0h
# B9 = 0x8F, B10 = 0x30, B11 = 0x00
sample_bytes = [0x00] * 21
sample_bytes[9] = 0x8F
sample_bytes[10] = 0x30
sample_bytes[11] = 0x00

decode_samsung_timers(sample_bytes)
```

## Verified Devices

This reverse engineering was tested and verified to work on the following hardware:
- **Samsung WindFree™ 1-Way Cassette** 
  - Model Numbers: `AC009BN1DCH` (9K Btu), `AC012BN1DCH` (12K Btu), `AC018BN1DCH` (18K Btu)

## Contribution
Discovered while building a custom local IR bridge for Hermes Agent. Feel free to use this algorithm to implement full dual-timer support in your own open-source IR libraries!



## License
This project is licensed under the [MIT License](LICENSE).
You are free to use, modify, and distribute this software, but it is provided "AS IS" with absolutely no liability or warranty.
