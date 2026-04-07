# UI, Functional Flows, and Test Cases

## 1) Purpose of This Document

This document explains:

- complete UI structure and screen behavior
- all major functional flows from user perspective
- practical, execution-ready test cases (manual + validation focus)

It is meant for project demo preparation, validation, and future maintenance.

---

## 2) UI Architecture Overview

The UI is built for a 160x128 ST7735 landscape display with rotary encoder input.

### 2.1 Screen Regions

The live screen is divided into four conceptual groups:

1. **Title/Status Group (top)**
   - app/context title
   - stability status text
   - status indicator color logic (unstable/settling/stable/locked)

2. **Weight Group (primary focus)**
   - large numeric weight display
   - unit display (`kg`)
   - high-contrast color for readability

3. **Info Group**
   - active profile name
   - active profile gravity value (`g`)
   - secondary metadata

4. **Action Bar (bottom)**
   - `Tare`
   - `Profile`
   - `Menu`
   - active action is highlighted

### 2.2 Menu Screen Pattern

All menus follow a common pattern:

- first item is always `Back` with icon
- rotary selects item (up/down)
- single click confirms selection
- long labels are wrapped across lines when needed

### 2.3 Visual and Interaction Principles

- dark background + bright text for white-backlight TFT readability
- consistent highlight color for selected controls
- minimal on-screen clutter
- no mandatory long-press navigation for primary flows

---

## 3) Input Model and Interaction Behavior

### 3.1 Rotary Encoder Mapping

- Clockwise (CW): move right/down/increment
- Counter-clockwise (CCW): move left/up/decrement
- Click: select/confirm

### 3.2 Input Priority

Encoder and button are interrupt-driven. Main loop drains input events first before render updates, reducing lag under rapid interaction.

### 3.3 Click Behavior Standard

All menu items should execute action on a **single click**. No double-click requirement is expected in final UX.

---

## 4) Functional Flows

## 4.1 Live Weighing Flow

1. System boots
2. Configuration and calibration load
3. Startup auto-tare waits for stable baseline then stores tare
4. Live weight updates with filtering and profile gravity scaling
5. Stability status changes based on noise/variance window
6. Stable weight may enter temporary locked display window

Expected result:
- smooth and readable weight display
- status transitions are understandable and deterministic

## 4.2 Tare Flow (Manual)

1. User selects `Tare` from action bar
2. System captures current baseline
3. Tare offset updates and saves to `calibration.json`
4. Display returns to live state

Expected result:
- weight near zero when scale is empty
- tare persists after reboot

## 4.3 Profile Selection Flow

1. User selects `Profile` action
2. Profile list opens (with `Back` at top)
3. User highlights a profile
4. Single click applies selection
5. Live screen updates profile name and gravity behavior

Expected result:
- selected profile is applied immediately
- displayed weight changes as per profile `g`

## 4.4 Profile Management Flow

Inside profile menu:

- add profile
- edit name
- edit gravity (`g`)
- delete profile (with confirmation)
- back navigation

Expected result:
- each action saves persistently to `profiles.json`
- deleted profile cannot be selected later

## 4.5 Global Menu Flow

Global menu should contain only global/system-level items:

- back
- recalibration
- display calibration
- select language

Expected result:
- no profile-specific edit actions here
- all items have complete action path and return path

## 4.6 Calibration Wizard Flow (Multi-Point)

1. Enter recalibration
2. Empty scale -> capture tare average
3. Place known weight -> capture averaged raw reading
4. Enter actual weight via encoder (50 g normal / 500 g fast)
5. Confirm add point
6. Ask add another point?
   - yes -> repeat place/input/confirm
   - no -> compute final scale factor (least-squares slope)
7. Save to `calibration.json`
8. Return to home/live

Expected result:
- better linear accuracy across range than single-point scaling

## 4.7 Language Change Flow

1. Open menu -> language
2. Select language option
3. UI strings update
4. Selection persists

Expected result:
- reboot should retain chosen language

---

## 5) Weight Computation and Status Behavior (User-Facing)

### 5.1 Practical Computation Steps

1. Read averaged raw value from HX711
2. Apply tare offset
3. Convert to base mass using calibration scale factor
4. Multiply by active profile `g`
5. Apply rounding and filtered display pipeline

### 5.2 Stability Status Intuition

- **Unstable**: high fluctuation
- **Settling**: moderate fluctuation
- **Stable**: low fluctuation over window
- **Locked**: stable value held for fixed duration for readability

---

## 6) Test Strategy

Use three levels:

1. **UI interaction tests** (encoder + menu behavior)
2. **Functional flow tests** (tare/profile/calibration/language)
3. **Measurement validation tests** (accuracy, repeatability, drift)

---

## 7) Detailed Test Cases

## 7.1 Boot and Initialization

### TC-B01: Boot to live screen
- Preconditions: valid firmware, display connected
- Steps:
  1. Power cycle board
  2. Observe startup and landing screen
- Expected:
  - no exception on boot
  - live screen visible
  - action bar visible with three actions

### TC-B02: Startup auto-tare persistence
- Preconditions: empty scale
- Steps:
  1. Power on and wait for startup stabilization
  2. Reboot
  3. Observe baseline behavior
- Expected:
  - baseline settles close to zero both runs
  - tare offset stored in `calibration.json`

## 7.2 Encoder and Input

### TC-I01: Direction mapping
- Steps:
  1. Rotate CW in menu and action bar
  2. Rotate CCW in menu and action bar
- Expected:
  - CW -> right/down/increase
  - CCW -> left/up/decrease

### TC-I02: Single-click activation
- Steps:
  1. Open menu
  2. Select each item with one click
- Expected:
  - action executes on first click
  - no double-click behavior

### TC-I03: Rapid rotation responsiveness
- Steps:
  1. Spin encoder quickly across multiple items
  2. Stop and click target item
- Expected:
  - no major lag
  - final selection reflects latest input

## 7.3 Menu and Navigation

### TC-M01: Back item consistency
- Steps:
  1. Open each menu/submenu
  2. Verify first item
  3. Click back
- Expected:
  - first item is back
  - returns to correct parent screen

### TC-M02: Long text wrapping
- Steps:
  1. Navigate to menus with long labels
  2. Observe rendering boundaries
- Expected:
  - text wraps to next line
  - no clipping outside visible menu area

## 7.4 Profile Flows

### TC-P01: Select existing profile
- Steps:
  1. Open profile list
  2. Select any non-active profile
- Expected:
  - profile switches immediately
  - info panel updates name and g

### TC-P02: Add profile persistence
- Steps:
  1. Add new profile with custom name and g
  2. Reboot
  3. Open profile list
- Expected:
  - profile exists after reboot
  - values are accurate

### TC-P03: Edit name and gravity
- Steps:
  1. Edit profile name
  2. Edit gravity value
- Expected:
  - no runtime attribute error
  - edited values apply and persist

### TC-P04: Delete profile confirmation
- Steps:
  1. Select delete profile
  2. Cancel once, confirm once
- Expected:
  - cancel keeps profile
  - confirm removes profile permanently

## 7.5 Calibration Flow

### TC-C01: Multi-point calibration completion
- Steps:
  1. Enter recalibration
  2. Capture tare
  3. Add 3 known points (e.g., 1.0, 2.5, 5.0 kg)
  4. Finish calibration
- Expected:
  - wizard reaches done state
  - values saved in `calibration.json`

### TC-C02: Fast-step input behavior
- Steps:
  1. Rotate slowly in weight input screen
  2. Rotate quickly in weight input screen
- Expected:
  - slow rotation step ~50 g
  - fast rotation step ~500 g

### TC-C03: Post-calibration accuracy spot check
- Steps:
  1. Place 1.0 kg, 2.5 kg, 5.0 kg known weights
  2. Record displayed values
- Expected:
  - bounded error across full range
  - no constant-factor distortion (e.g., 4x)

## 7.6 Measurement Stability

### TC-S01: Stability indicator transitions
- Steps:
  1. Keep empty scale
  2. Add weight abruptly
  3. Wait until stable
- Expected:
  - status moves unstable -> settling -> stable
  - indicator colors follow expected mapping

### TC-S02: Locked display hold
- Steps:
  1. Place fixed weight
  2. Wait until stable
  3. Observe lock duration
- Expected:
  - locked state appears after stability criteria
  - display holds locked value for configured freeze time
  - normal updates resume afterward

## 7.7 Persistence and Recovery

### TC-R01: Calibration persistence
- Steps:
  1. Complete calibration
  2. Reboot
  3. Measure known weight
- Expected:
  - calibration retained
  - no mandatory recalibration each boot

### TC-R02: Tare persistence (manual + auto)
- Steps:
  1. Perform manual tare and reboot
  2. Confirm auto-tare path and reboot
- Expected:
  - both tare paths write persistent offset

## 7.8 Display/Color Validation

### TC-D01: Color channel correctness
- Steps:
  1. Run `test_lcd_colors.py`
  2. Inspect RGB bars/labels
- Expected:
  - red/green/blue appear correct (no channel rotation)

### TC-D02: Main UI color readability
- Steps:
  1. Run main app in standard lighting
  2. Inspect contrast and legibility
- Expected:
  - white/yellow/pink text readable on dark background

---

## 8) Acceptance Criteria (Project-Level)

Project is considered acceptable for demo/release if:

1. All core flows complete without crash
2. Single-click navigation works consistently
3. Calibration and tare persist after reboot
4. Profile management is complete and persistent
5. Measured values show expected monotonic and near-linear behavior
6. UI remains readable and responsive on target hardware

---

## 9) Demo Sequence Recommendation (College Evaluation)

1. Boot and show live UI
2. Switch profile Earth -> Moon -> Jupiter
3. Show tare action and near-zero reset
4. Run quick multi-point recalibration (2-3 points)
5. Verify with known weights
6. Show language switch and reboot persistence
7. Run color test utility briefly to demonstrate display correctness troubleshooting

---

## 10) Notes for Future Test Automation

Although current validation is mostly manual (hardware-in-loop), automation can be increased by:

- mocking encoder event stream for deterministic UI state tests
- unit tests for calibration fit and filter functions
- regression scripts for profile JSON read/write and schema checks

This reduces risk when tuning constants (sampling window, thresholds, redraw period).

