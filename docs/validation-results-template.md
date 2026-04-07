# Validation Results Template

## Project
- Title:
- Team/Student:
- Date:
- Firmware snapshot:
- Hardware setup ID:

---

## 1) Environment Record

- Pico supply method:
- Ambient conditions:
- Platform/mechanical notes:
- Known weights used:
- Display module model:
- Load cell capacity/spec:

---

## 2) Functional Test Log

| Test ID | Scenario | Expected | Actual | Pass/Fail | Notes |
|---|---|---|---|---|---|
| B01 | Boot to live screen | No crash, live UI |  |  |  |
| I01 | Encoder CW/CCW mapping | CW right/down, CCW left/up |  |  |  |
| I02 | Single click menu selection | One click triggers action |  |  |  |
| M01 | Back item in all menus | Back shown first |  |  |  |
| P01 | Profile select | Selection applies immediately |  |  |  |
| P02 | Profile add persistence | Survives reboot |  |  |  |
| P03 | Profile edit name/g | Updates and persists |  |  |  |
| P04 | Profile delete confirm | Delete on confirm only |  |  |  |
| C01 | Multi-point calibration flow | Completes and saves |  |  |  |
| L01 | Language switch | UI language updates and persists |  |  |  |
| R01 | Tare persistence | Manual + startup tare retained |  |  |  |
| D01 | Color channel test | RGB appears correct |  |  |  |

---

## 3) Measurement Accuracy Table

Fill at least 3-5 reference points.  
Formula:
- Absolute Error = Displayed - Reference
- Percent Error = (Absolute Error / Reference) x 100

| Point | Reference (kg) | Trial 1 (kg) | Trial 2 (kg) | Trial 3 (kg) | Mean Display (kg) | Abs Error (kg) | % Error |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 |  |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |
| 4 |  |  |  |  |  |  |  |
| 5 |  |  |  |  |  |  |  |

---

## 4) Repeatability Assessment

Take one fixed reference weight and place/remove repeatedly.

| Trial | Displayed (kg) |
|---|---:|
| 1 |  |
| 2 |  |
| 3 |  |
| 4 |  |
| 5 |  |
| 6 |  |
| 7 |  |
| 8 |  |
| 9 |  |
| 10 |  |

Computed:
- Mean:
- Max deviation from mean:
- Std. deviation (optional):

---

## 5) Drift Test (No-Load)

Keep scale empty and log value over time.

| Time | Displayed (kg) | Stability State |
|---|---:|---|
| 0 min |  |  |
| 2 min |  |  |
| 4 min |  |  |
| 6 min |  |  |
| 8 min |  |  |
| 10 min |  |  |

Observation:
- drift band:
- acceptable?:

---

## 6) Stability and Lock Behavior

| Scenario | Expected | Observed |
|---|---|---|
| sudden load placement | unstable -> settling -> stable |  |
| stable hold | transitions to locked |  |
| lock duration | holds near configured freeze ms |  |
| post-lock | returns to live updates |  |

---

## 7) Calibration Session Record

- Calibration date/time:
- Profile used during calibration:
- Captured tare raw:
- Number of points:

| Point | Raw (avg) | Entered weight (kg) |
|---|---:|---:|
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |
| 4 |  |  |
| 5 |  |  |

Saved values:
- `offset`:
- `scale_factor`:

---

## 8) Issue Tracker During Validation

| Issue ID | Symptom | Repro steps | Severity | Status | Resolution |
|---|---|---|---|---|---|
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

---

## 9) Final Sign-Off

- Functional tests completed: Yes/No
- Measurement validation completed: Yes/No
- Major blockers remaining: Yes/No
- Ready for demo: Yes/No

Reviewer Name:
Signature:
Date:

