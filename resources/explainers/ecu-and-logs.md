# Car, ECU and log files

## Car

- **Car:** RNU12 Bluebird, 4WD, 5-speed manual. About 1450 kg, plus a 100 kg driver.
- **Engine:** Nissan CA18DET, under 10,000 km on the build. Compression is even at 143–145 psi per cylinder.
- **Build:** CP forged pistons (8.5:1), H-beam rods, 2mm MLS head gasket, ARP head studs, 660cc injectors, upgraded fuel pump and FPR, Audi R8 coils, GT28/25 hybrid turbo, FMIC, steel intercooler piping (probably 2.5").
- **Fuel:** 100 RON.
- **Static timing:** 10° BTDC. Total timing = ignition table value + 10°.
- **Drivetrain:** gearbox 3.285 / 1.850 / 1.272 / 0.954 / 0.795, reverse 3.428. Final drive most likely 4.421: it reads just under 3000 rpm at an indicated 100 km/h in 5th, and 4.421 gives 3060 rpm at a true 100 (4.11 would give 2840). Tyres 215/45R17, about 0.305 m rolling radius.
- **Rev limit:** stock is 7500 rpm. The tunes' R.LIM of 6700 was caution on a newish engine.
- **Boost:** has run 18 psi, backed down to 16 psi because it surged in first gear. No log in `resources/` reaches 16 psi; the highest is 13.3 psi.

## ECU

- **Model:** Link LEM V5, tuned with PCLink V2.5 (8/12/04). The comms logs name it "LEM V5".
- **Load:** MAP-based (speed-density). Pulse width scales with fuel number × MAP.
- **MAP range:** MAP is a 1-byte value in kPa, so the ECU can't read above 255 kPa (22 psi). The tables stop at the 210–240 kPa row (about 20 psi).
- **Closed loop:** lambda is off in every tune, so AFR never self-corrects.
- **Knock control:** none.

## What's in `resources/`

| Path | Contents |
|---|---|
| `ecu_config_files/l1.pcl` | Tune read by `knockai/decode.py`. Undated, not identical to any tune in the zips; closest to `fine-01.pcl`, so the newest by content. No log covers it. |
| `runs/r02/` | `r02.pcl` and the four `r2-*` logs. Same files as in `r01.zip`. |
| `link files.zip` | 3 Jan – 10 Mar 2021. Tunes `33`, `331`, `331-ign`, `332`, `332-ign`, `333-boost`, `333-boost-fuel`, `dan-1`–`dan-4`; 13 run logs; comms logs `Log0`, `Log1`; Link's own samples (`LinkPlusSample.pcl`, `SampleOne.pcl`, `PCLink_RuntimeSample.txt`). |
| `r01.zip` | 7 Jun 2021. Tunes `r01`, `r02`, `r03`, `r03-backfire`, `r03-backfire2`; 10 run logs; comms logs `Log0`–`Log2`; `PCLink_cfg.ini`; `LDLR`. |
| `fine-01-pipeoff.zip` | 12 Jun 2021. Tune `fine-01.pcl` and log `fine-01-pipeoff.txt`. Pipe-off run; not used for analysis. |

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
- **`TPS`:** 20 is closed, 100 is wide open.
- **`WB_Oxy`:** wideband air-fuel ratio. It lags the engine by about 0.3 s (`notebooks/af_response.ipynb`).
- **`WG_DC`:** wastegate solenoid duty, %.
- **`Zone`:** the table cell in use. See below.
- **`Ign_Adv`:** table advance. Add 10° static for total timing.
- **`Boost_`:** 0.0 in every log. Use `MAP` for boost.
- **`Markers`:** `I` in every row. No run has markers set.

## Tunes (`*.pcl`)

PCLink tune file with sections `[ConfigByteSize]`, `[Memo]`, `[ConfigData]`, `[LinkMemData]`, `[CheckSum]`.

`[LinkMemData]` is 744 comma-separated byte values: the ECU memory image. List index = ECU memory location (MemLoc). Values are raw bytes.

| MemLoc | Setting |
|---|---|
| 1 | MASTER (100 in every tune) |
| 5 | IAT Fuel |
| 15 | Oxygen Target |
| 19 | Base Timing |
| 20 | IAT Retard |
| 21 | Dwell |
| 25 | R.LIM, RPM limit in hundreds (67 = 6700 rpm) |
| 26 | M.LIM, MAP limit in kPa. The ECU cuts fuel at it: in `r3-backfire` and `r3-backfire2` (M.LIM 180) `INJ_PW` went to 0 at 180–181 kPa, the wideband spiked to 13.7–18.3 and it backfired. Set deliberately conservative as overboost protection. |
| 33 | Mode byte. Bit 0 lambda off/on; bits 1–2 table row axis (MAP, TPS, Vacuum, TPS+MAP); bits 3–4 Aux1 function (RPM SW, Idle Speed, Boost Control); bit 5 IAT control off/on; bit 6 boost mode (Simple, Advanced). |
| 35 | ORUN VAC |
| 45 | Boost Target |
| 46 | Wastegate Base |
| 47 | Wastegate Sens. |
| 48 | Wastegate Hold |
| 60–219 | FuelTable160 (8 rows × 20 columns) |
| 220–259 | Split Table V5 (40 cells) |
| 260–419 | IgnTable160 (8 rows × 20 columns) |

The full map is in the comms logs.

## How the ECU reads the tables

Both tables are 8 MAP rows × 20 RPM columns, stored row by row (`decode.py`'s 8×20 reshape is correct). Row 0 is the lowest MAP.

- **`Zone` in the logs:** hundreds = MAP row + 1, then (column × 5). Zone 645 is row 5, column 9.
- **Cell bands:** each row covers 30 kPa and each column 500 rpm.
- **Interpolation:** the ECU interpolates bilinearly between sites at the cell centres: MAP 15, 45 … 225 kPa and RPM 250, 750 … 9750. Checked against logged ignition: 70% of samples exact, mean error 0.5°. A plain cell lookup gets 48% and 0.9°.

| Row | Zone | MAP band (kPa) | Site (kPa) | Site boost (psi) |
|---|---|---|---|---|
| 0 | 1xx | 0–30 | 15 | vacuum |
| 1 | 2xx | 30–60 | 45 | vacuum |
| 2 | 3xx | 60–90 | 75 | vacuum |
| 3 | 4xx | 90–120 | 105 | 0.5 |
| 4 | 5xx | 120–150 | 135 | 4.9 |
| 5 | 6xx | 150–180 | 165 | 9.2 |
| 6 | 7xx | 180–210 | 195 | 13.6 |
| 7 | 8xx | 210–240 | 225 | 17.9 |

- **Fuel:** `INJ_PW` ≈ 0.000517 × fuel number × MAP + 0.14 ms (fit on the warm June logs, mean error 0.08 ms). The fuel table is VE-style: to move a cell's AFR, scale it by measured AFR ÷ target AFR.
- **Injector duty:** `INJ_DC` % ≈ `INJ_PW` (ms) × RPM ÷ 1200. The injectors fire once per cycle.

## Comms logs (`Log*.log`)

PCLink's serial comms log, with every byte XORed with `0x33`:

```python
text = bytes(b ^ 0x33 for b in open(path, 'rb').read()).decode('latin1')
```

- **Connection header:** PCLink version, then the ECU memory map. One line per MemLoc with `CRovNum`, `ByteSize` and the setting name; mode bytes are broken down bit by bit.
- **Body:** `RetrieveBlockData` lines, the 24-byte live data packets PCLink polled.
- **Live edits:** every value written to the ECU is a `Program L2: Addr:<MemLoc>, Data:<value>` line, in order, without timestamps. `r01/Log1.log` shows Wastegate Base swept from 30 to 48, M.LIM raised to 200 before the homerun (which is why that run reached 186 kPa without a cut) and Wastegate Base set back to 0 at the end.
- **`PCLink_cfg.ini`:** PCLink settings. COM2, 14400 baud.

## Tune history

| Tune | Saved | Change from the previous tune |
|---|---|---|
| `33` | 2021-01-03 16:22 | Starting point. M.LIM 170, Boost Target 135, Wastegate Base 10, boost mode Advanced, R.LIM 70. |
| `331` | 01-03 18:02 | 60 fuel cells. |
| `331-ign` | 01-03 18:04 | 160 ignition cells. |
| `332` | 01-03 18:07 | 60 fuel cells. |
| `332-ign` | 01-03 18:17 | 160 ignition cells. |
| `333-boost` | 01-03 18:33 | Boost Target 135 → 168; Accel Low 10 → 8, Accel High 20 → 17. |
| `333-boost-fuel` | 01-03 18:39 | 100 fuel cells; Boost Target 168 → 160. |
| `dan-1` | 03-08 19:54 | 8 fuel cells, 1 ignition cell. |
| `dan-2` | 03-08 20:04 | 49 ignition cells. |
| `dan-3` | 03-08 20:15 | 40 fuel cells, 21 ignition cells. |
| `dan-4` | 03-10 05:58 | M.LIM 170 → 179; boost mode Advanced → Simple; Boost Target 160 → 170. |
| `r01` | 06-07 15:37 | 72 fuel cells; Cold Crank 8 → 10; Accel High 17 → 14; R.LIM 70 → 67; Wastegate Base 10 → 0. |
| `r02` | 06-07 16:19 | 5 fuel cells. |
| `r03` | 06-07 16:39 | 56 fuel cells leaner by 1–16, all in rows 0–3. |
| `r03-backfire` | 06-07 16:43 | Wastegate Base 0 → 35; M.LIM 179 → 180. |
| `r03-backfire2` | 06-07 16:46 | Wastegate Base 35 → 37. |
| `fine-01` | 06-12 18:08 | 9 fuel cells, 2 ignition cells; M.LIM 180 → 207; Wastegate Base 37 → 41. |
| `l1` | undated | 132 fuel cells (boost rows leaner, high-RPM columns flattened), 105 ignition cells; COLD 38 → 10; Accel Low 8 → 7; Dwell 30 → 28; Wastegate Base 41 → 38; Fan 90 → 94. |

Every tune from `dan-4` on has Aux1 set to Boost Control and Boost Target 170.

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

Runs with 0% wastegate duty peak at 7.2–7.8 psi, apart from the boost-leak run.

## `l1.pcl` checked against the June logs

AFR figures are the 7 Jun `r2`/`r3` logs (warm, no accel enrichment, no overrun cut, wideband lag removed) projected onto `l1`'s fuel table. No log goes above 210 kPa or 6700 rpm, so those parts of both tables have never been checked.

- **Boost fuel:** 11.1–11.7 AFR at full throttle from 120 kPa up. Richest (11.1) at 3000–4000 rpm and above 5500 rpm at 165 kPa and up; leanest (11.6–11.7) at 4500–5000 rpm. Target is 11.5 (older engine, dated components), so boost fuel is within about ±3%.
- **Top fuel row:** the 225 kPa row (110) carries 5% more fuel than the 195 kPa row, so `l1` projects to about 11.0 AFR at 16 psi and 10.8 at 18 psi.
- **Cruise fuel:** 12.1–12.9 AFR at 45–75 kPa, 3250–4250 rpm, light throttle. Getting to 14.7 would take out 12–17%.
- **75 kPa row:** jumps 88 → 97 between 4250 and 4750 rpm, the biggest RPM-direction step in the table, with no data there.
- **Idle:** 14.2–14.4 AFR.
- **Timing origin:** the ignition table was copied from an image of a stock CA18 table. The 195 and 225 kPa rows are flat fill-ins: a stock table never sees 14–18 psi. The factory ECU also measures load with an airflow meter, not MAP, and pulls timing on knock; the LEM V5 does neither.
- **Total timing, 3000–6500 rpm:**

  | MAP | Boost | Total |
  |---|---|---|
  | 15 kPa | vacuum | 45° |
  | 45 kPa | vacuum | 42° |
  | 75 kPa | vacuum | 35–36° |
  | 105 kPa | 0 psi | 26° |
  | 135 kPa | 5 psi | 20–23° |
  | 165 kPa | 9 psi | 19–22° |
  | 195 kPa | 14 psi | 14° flat |
  | 225 kPa | 18 psi | 13° flat |

  Idle is 30° total; the June tunes ran 22–24°. There's a dip to 25–27° at 1250 rpm under light load, between 30° and 35°.
- **Timing shape:**
  - The 9 psi row is only 1° below the 5 psi row and 5–8° above the 14 psi row.
  - Against the rule of thumb of 1° less per psi from 26° at 0 psi, the table is on the rule at 5 psi and 2–5° ahead from 9 psi up.
  - The 5 and 9 psi rows gain 2–3° from 3000 to 6500 rpm; the 14 and 18 psi rows don't change with RPM.
  - CA18s like boost and revs rather than timing. On 100 RON the stock-derived rows have more knock margin than in the factory car. The rich boost AFR is likely part of the knock margin, so don't lean it without knock monitoring.

## Injectors and boost ceiling

- **Injector duty:** 660cc, projected on `l1` at 11.5 AFR.

  | RPM | 16 psi | 18 psi | 20 psi |
  |---|---|---|---|
  | 7500 | 72% | 76% | 81% |
  | 8000 | 77% | 81% | 86% |

  With `l1` fuel as it stands (richer), 6700 rpm is 67% at 16 psi and 72% at 18 psi.
- **Airflow needed:** 1.809 L, cylinder-filling efficiency 0.85–0.9 (0.82–0.94 measured at 11 psi from fuel flow × AFR), 25 °C intake.

  | RPM | 16 psi | 18 psi | 20 psi |
  |---|---|---|---|
  | 6700 | 28–30 lb/min | 30–32 lb/min | 32–34 lb/min |
  | 7500 | 31–34 lb/min | 34–36 lb/min | 36–38 lb/min |
  | 8000 | 33–36 lb/min | 36–38 lb/min | 38–41 lb/min |

  Pressure ratio is about 2.2, 2.35 and 2.5 for 16, 18 and 20 psi. Check against the compressor map for the hybrid's wheel; these are at the upper end for a GT28-class compressor. Absolute figures are good to about ±10–15%.
- **Piping and intercooler:** 2.5" is good for 45–50 lb/min, so not a limit. The FMIC holds intake temperature at 14–22 °C at 11 psi in the June logs (winter).
- **Ceiling:** about 18–20 psi. The ECU tops out around 20–22 psi, the injectors around 20–21.5 psi at 11.5 AFR and 7500 rpm, and the turbo likely lands in the same range at high RPM. The bottom end, head gasket and studs go past all of these.
- **8000 rpm:** the bottom end will take it. The limits are the valvetrain, the injectors (ceiling back to about 18–20 psi) and the turbo (36–38 lb/min at 18 psi). Log a pull past 7000 rpm to see whether airflow still climbs.

## Power estimate

About **215–220 hp at the wheels at 11–12 psi** and 170–200 at 7.5 psi, from 1st and 2nd gear pulls.

- **Method:** wheel power = (effective mass × acceleration + rolling resistance + drag) × speed, with speed and acceleration from RPM through the gear, final drive and tyre.
  - Mass 1570 kg (car, 100 kg driver, 30 L fuel); rotating-mass factor 1.04 + 0.0025 × overall ratio².
  - Rolling resistance 0.015; drag area 0.65 m².
  - RPM smoothed with a quadratic fit per pull. Power is read at 5000–5750 rpm.
- **Pulls used:** 7.5 psi from `r2-goodpull`, `r2-goodpull2`, `r2-100k-af`, `r3-100k-af` and `r3-100k-af-1`; 11–12 psi from `r3-backfire2` and `r3-homerun-varyingboost`.
- **3rd and 4th gear pulls:** they read 20–35% lower on the same runs. That's systematic, most likely road gradient, so they're left out.
- **Sensitivity:** power scales with the overall ratio squared. The 4.11 final drive would give 240–250 hp at the wheels at 11–12 psi.
- **Cross-check:** the airflow method (fuel flow × AFR, 9–10 hp per lb/min, 20–25% 4WD drivetrain loss) gives 150–190 hp at the wheels at 11–12 psi, maybe 10% more if fuel pressure runs above the injectors' 3 bar rating.
- **Where the rest is:** `l1`'s maps leave little on the table (about 1 hp from flattening boost AFR to 11.5). The remaining power is in boost and revs.
