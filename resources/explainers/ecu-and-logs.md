# Car, ECU and log files

## Car and ECU

- **Engine:** Nissan CA18DET in an RNU12 Bluebird (4WD, manual).
- **ECU:** Link LEM V5, tuned with PCLink V2.5 (8/12/04). The comms logs name it "LEM V5".
- **Boost:** has run 18 psi, backed down to 16 psi because it surged in first gear. No log in `resources/` reaches 16 psi; the highest is 13.3 psi.

## What's in `resources/`

| Path | Contents |
|---|---|
| `ecu_config_files/l1.pcl` | Tune read by `knockai/decode.py`. Not identical to any tune in the zips. |
| `runs/r02/` | `r02.pcl` and the four `r2-*` logs. Same files as in `r01.zip`. |
| `link files.zip` | 3 Jan – 10 Mar 2021. Tunes `33`, `331`, `331-ign`, `332`, `332-ign`, `333-boost`, `333-boost-fuel`, `dan-1`–`dan-4`; 13 run logs; comms logs `Log0`, `Log1`; Link's own samples (`LinkPlusSample.pcl`, `SampleOne.pcl`, `PCLink_RuntimeSample.txt`). |
| `r01.zip` | 7 Jun 2021. Tunes `r01`, `r02`, `r03`, `r03-backfire`, `r03-backfire2`; 10 run logs; comms logs `Log0`–`Log2`; `PCLink_cfg.ini`; `LDLR`. |
| `fine-01-pipeoff.zip` | 12 Jun 2021. Tune `fine-01.pcl` and log `fine-01-pipeoff.txt`. |

Unpack each zip to a folder of its own name (the zips hold the same file names, e.g. `Log0.log`):

```sh
cd resources
unzip r01.zip -d r01
unzip fine-01-pipeoff.zip -d fine-01-pipeoff
unzip "link files.zip"    # already contains a "link files/" folder
```

## Run logs (`*.txt`)

PCLink datalog export. Tab-separated, every line ends in `;`.

- **Line 1–4:** `TableSize`, the column count (`28`), `CRNum` (PCLink parameter ID per column), column names. `LDLR` in `r01.zip` is this header on its own.
- **Rows:** one sample about every 0.09 s.
- **Columns:** `Secs RPM MAP ETemp IAT VOLTS TPS OXY WB_Oxy INJ_PW INJ_DC Boost_ WG_DC ISC_DC Zone Ign_Adv SCE MAPLim RPMLim Accel_ RadFan Aux1 Aux1 Orun_Vac Iat_Rtd Stagin IDLEST TPSCls Markers`. `Aux1` appears twice.
- **Layout:** every run log here has this layout, and `knockai/log_decode.py` reads it. `PCLink_RuntimeSample.txt` (Link's 2004 sample) has 29 columns in a different order.
- **`MAP`:** kPa absolute (about 32 at idle).
- **`WB_Oxy`:** wideband air-fuel ratio.
- **`WG_DC`:** wastegate solenoid duty, %.
- **`Boost_`:** 0.0 in every log. Use `MAP` for boost.
- **`Markers`:** `I` in every row. No run has markers set.

## Tunes (`*.pcl`)

PCLink tune file with sections `[ConfigByteSize]`, `[Memo]`, `[ConfigData]`, `[LinkMemData]`, `[CheckSum]`.

`[LinkMemData]` is 744 comma-separated byte values: the ECU memory image. List index = ECU memory location (MemLoc). Values are raw bytes.

| MemLoc | Setting |
|---|---|
| 25 | R.LIM (RPM limit) |
| 26 | M.LIM (MAP limit) |
| 33 | Mode byte. Bit 0 lambda off/on; bits 1–2 table row axis (MAP, TPS, Vacuum, TPS+MAP); bits 3–4 Aux1 function (RPM SW, Idle Speed, Boost Control); bit 5 IAT control off/on; bit 6 boost mode (Simple, Advanced). |
| 45 | Boost Target |
| 46 | Wastegate Base |
| 47 | Wastegate Sens. |
| 48 | Wastegate Hold |
| 60–219 | FuelTable160 (160 cells; `decode.py` reshapes to 8×20) |
| 220–259 | Split Table V5 (40 cells) |
| 260–419 | IgnTable160 (160 cells; `decode.py` reshapes to 8×20) |

The full map is in the comms logs.

## Comms logs (`Log*.log`)

PCLink's serial comms log, with every byte XORed with `0x33`:

```python
text = bytes(b ^ 0x33 for b in open(path, 'rb').read()).decode('latin1')
```

- **Connection header:** PCLink version, then the ECU memory map. One line per MemLoc with `CRovNum`, `ByteSize` and the setting name; mode bytes are broken down bit by bit.
- **Body:** `RetrieveBlockData` lines, the 24-byte live data packets PCLink polled.
- **`PCLink_cfg.ini`:** PCLink settings. COM2, 14400 baud.

## Boost

Boost psi = (MAP − 101.3) × 0.145.

| Date | Log | Length (s) | Peak MAP (kPa) | Peak boost (psi) | Max WG_DC (%) |
|---|---|---|---|---|---|
| 2021-01-03 | `link files/1st run.txt` | 272 | 154 | 7.6 | 100 |
| 2021-01-03 | `link files/run 2.txt` | 30 | 152 | 7.4 | 100 |
| 2021-01-03 | `link files/dplot-1.txt` | 31 | 40 | −8.9 | 0 |
| 2021-01-03 | `link files/dplot-2.txt` | 91 | 151 | 7.2 | 100 |
| 2021-01-03 | `link files/dbplot-died.txt` | 41 | 143 | 6.0 | 100 |
| 2021-01-03 | `link files/dplot-3pull.txt` | 89 | 152 | 7.4 | 100 |
| 2021-01-03 | `link files/dplot-3pull-long.txt` | 1066 | 152 | 7.4 | 100 |
| 2021-03-08 | `link files/d-run1-knocking4k.txt` | 165 | 151 | 7.2 | 100 |
| 2021-03-08 | `link files/d-run2-noknocking4k.txt` | 167 | 160 | 8.5 | 100 |
| 2021-03-08 | `link files/d-run3-clear-runs.txt` | 233 | 158 | 8.2 | 100 |
| 2021-03-08 | `link files/d-run3-pushstart-runs.txt` | 133 | 171 | 10.1 | 100 |
| 2021-03-08 | `link files/d-run4.txt` | 114 | 152 | 7.4 | 10 |
| 2021-06-07 | `r01/r1-1boostleak.txt` | 229 | 130 | 4.2 | 0 |
| 2021-06-07 | `r01/r2-goodpull.txt` | 128 | 155 | 7.8 | 0 |
| 2021-06-07 | `r01/r2-goodpull2.txt` | 26 | 155 | 7.8 | 0 |
| 2021-06-07 | `r01/r2-slowride.txt` | 74 | 151 | 7.2 | 0 |
| 2021-06-07 | `r01/r2-100k-af.txt` | 138 | 154 | 7.6 | 0 |
| 2021-06-07 | `r01/r3-100k-af.txt` | 167 | 154 | 7.6 | 0 |
| 2021-06-07 | `r01/r3-100k-af-1.txt` | 53 | 153 | 7.5 | 0 |
| 2021-06-07 | `r01/r3-backfire.txt` | 121 | 181 | 11.6 | 41 |
| 2021-06-07 | `r01/r3-backfire2.txt` | 170 | 181 | 11.6 | 38 |
| 2021-06-07 | `r01/r3-homerun-varyingboost.txt` | 134 | 186 | 12.3 | 48 |
| 2021-06-12 | `fine-01-pipeoff/fine-01-pipeoff.txt` | 98 | 193 | 13.3 | 40 |

## r02 → r03 tune changes (`r01.zip`)

| Tune | Change from the previous tune |
|---|---|
| `r03` | 56 fuel cells leaner by 1–16, all in rows 0–3 of the 8×20 fuel table. Ignition unchanged. |
| `r03-backfire` | Wastegate Base 0 → 35; M.LIM 179 → 180. Fuel and ignition unchanged. |
| `r03-backfire2` | Wastegate Base 35 → 37. Fuel and ignition unchanged. |

All four tunes have Aux1 set to Boost Control, boost mode Simple, Boost Target 170.
