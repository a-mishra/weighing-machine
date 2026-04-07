# Viva Q&A (Likely Examiner Questions)

## 1) Project Fundamentals

### Q1. What is the core objective of your project?
To build a smart weighing machine on Pico 2W that measures weight from load-cell signals and also simulates displayed weight under different gravity profiles (Earth, Moon, Jupiter, etc.).

### Q2. Why is this a good minor project?
It combines hardware interfacing, embedded software architecture, filtering, state-machine UI, persistence, and practical debugging under resource constraints.

---

## 2) Sensor and Calibration

### Q3. Why is calibration needed?
HX711 gives raw ADC counts, not kg directly. Calibration maps raw counts to physical mass by estimating offset (tare) and scale factor.

### Q4. Why did you use multi-point calibration instead of single-point?
Multi-point fitting improves linearity over a range and reduces sensitivity to one bad capture point.

### Q5. What math is used in calibration?
A fixed-offset least-squares slope fit:
- `raw - tare = scale_factor * base_mass`
- `scale_factor = sum(base_mass * raw_delta) / sum(base_mass^2)`

### Q6. Why is calibration base modeled at g=1?
It creates one consistent mass baseline. Any profile display is then `displayed_weight = base_mass * profile_g`.

---

## 3) Filtering and Stability

### Q7. Why are readings unstable without filtering?
Load cells and analog front-end are sensitive to vibration, electrical noise, and mechanical micro-movements.

### Q8. Which filters are used?
Moving average/median utilities are available, and runtime display is primarily EMA-based for lower CPU cost with smooth response.

### Q9. How do you detect stable vs unstable?
Using spread of recent window:
- low spread -> stable
- medium spread -> settling
- high spread -> unstable

### Q10. What is locked status?
After consecutive stable cycles, displayed value is frozen for a configured duration to improve readability and reduce flicker.

---

## 4) UI and Input

### Q11. How is the UI structured?
Four regions:
1) title/status, 2) large weight display, 3) profile info, 4) action bar.

### Q12. Why use a rotary encoder?
It gives compact 3-action control (CW/CCW/click) suitable for small embedded UI without touchscreen.

### Q13. Is user input polling or interrupt based?
Input capture is interrupt-based. Events are buffered in an IRQ-safe structure and consumed in main loop.

### Q14. Why is interrupt safety important in MicroPython?
Allocations or heavy work inside ISR can cause missed events or instability. So ISR code is kept constant-time and allocation-light.

---

## 5) Software Architecture

### Q15. Why did you choose a state machine?
It keeps behavior deterministic. Each screen/state has clear event rules and transitions, reducing accidental cross-flow bugs.

### Q16. How is persistence implemented?
`profiles.json` stores profiles/language. `calibration.json` stores tare and scale factor. Files are loaded on startup and updated on relevant actions.

### Q17. What happens on startup?
Splash -> auto-tare attempt on stable empty scale -> live operation loop.

---

## 6) Performance and Optimization

### Q18. Why did UI feel laggy earlier?
Full-frame redraw and sensor work can consume CPU. If done every loop, input response can degrade.

### Q19. How did you improve responsiveness?
Main loop prioritizes draining input events first and redraws only on events or periodic timeout (`UI_REDRAW_MS`).

### Q20. Any memory-related optimization done?
Yes. Display color-byte correction is done via in-place byte swap in framebuffer push to avoid duplicate full-size buffer allocation.

---

## 7) Hardware Debugging Questions

### Q21. What caused wrong display colors during development?
RGB565 byte-order mismatch between framebuffer representation and panel expectation.

### Q22. How did you verify it?
Using a dedicated script (`test_lcd_colors.py`) and then validating corrected behavior in main application UI.

### Q23. What are common practical issues with load cells?
Drift, mechanical creep, off-center loading error, loose mounting, and electrical noise.

---

## 8) Validation and Results

### Q24. How did you validate correctness?
By running functional test flows, known-weight accuracy checks, repeatability tests, drift tests, and persistence checks after reboot.

### Q25. What metrics did you track?
Absolute error, percent error, repeatability spread, drift band, and UI responsiveness observations.

---

## 9) Limitations and Future Scope

### Q26. Current limitations?
- manual hardware calibration dependency
- environmental sensitivity of analog sensors
- full-frame rendering overhead on small MCU

### Q27. Future improvements?
- partial/dirty-rect rendering
- richer automated tests
- additional diagnostics counters
- optional cloud dashboards and logging analytics

---

## 10) Short Closing Answer

If examiner asks for one-line summary:

"This project turns noisy analog load-cell data into a stable, user-friendly weighing interface using interrupt-driven input, multi-point calibration, and persistent configuration on constrained embedded hardware."

