# Professor Viva Master Questions Guide

## 1) How to Use This File

This document is designed as a complete viva preparation set.  
Read in this order:

1. Basic concept questions
2. Design and architecture questions
3. Math and calibration questions
4. Debugging and practical questions
5. Validation and future scope questions

Tip: Practice answers in your own words, but keep technical terms exact.

---

## 2) One-Minute Project Pitch (Memorize)

"My project is a smart weighing machine built on Raspberry Pi Pico 2W with HX711 and load cell. It provides stable weight display using filtering, supports multi-point calibration, profile-based gravity simulation (Earth/Moon/Jupiter/custom g), interrupt-driven encoder UI, and persistent storage for calibration and profiles. I designed it with a state-machine architecture to keep flows deterministic on constrained hardware."

---

## 3) Basic Questions (Foundation)

### Q1. What problem does your project solve?
It converts noisy raw load-cell signals into practical, stable, user-friendly weight readings with configurable profiles and persistent calibration.

### Q2. Why did you choose Raspberry Pi Pico 2W?
It is low cost, reliable for GPIO-heavy embedded work, supports MicroPython fast prototyping, and is sufficient for HX711 + TFT + encoder integration.

### Q3. What are the major hardware components?
- Pico 2W
- HX711 + load cell
- ST7735 TFT display
- rotary encoder with switch
- optional buzzer

### Q4. Why use HX711?
Load cells output very small analog signals. HX711 provides high-gain instrumentation amplification and ADC conversion suitable for weight sensing.

### Q5. What is unique in your project compared to basic digital scales?
- multi-point calibration
- profile-based gravity simulation
- graphical menu UI
- persistent profile and calibration data
- practical stability status and lock behavior

---

## 4) Architecture Questions

### Q6. Explain your software architecture in layers.
- Driver layer: HX711 and ST7735 low-level handling
- Module layer: scale math, encoder events, profile store, language
- App layer (`main.py`): state machine, event dispatch, rendering orchestration

### Q7. Why did you use a state machine?
Each screen and flow has explicit behavior (`cw`, `ccw`, `click`, `long`), so transitions are deterministic and easier to test/debug.

### Q8. What are the key states?
- live
- menu / profile_menu / language_menu
- edit_name / edit_g
- select_profile / confirm_delete
- calibration states: cal_tare, cal_place, cal_input, cal_confirm, cal_done

### Q9. How are modules decoupled?
`main.py` coordinates modules via clean interfaces:
- `scale.read_filtered_kg()`
- `encoder.poll()`
- `store.*` profile operations
- `ui.draw_*()` rendering per state

---

## 5) Input and Real-Time Behavior Questions

### Q10. Is input interrupt-based or polling-based?
Input capture is interrupt-based in `modules/encoder.py`. Events are buffered and consumed in main loop.

### Q11. Why not do everything directly in ISR?
MicroPython ISR context should avoid heap allocations and heavy logic. So ISR stores compact events, and expensive work is done outside ISR.

### Q12. How did you improve responsiveness?
- drain input queue before rendering
- redraw only on event or periodic timer (`UI_REDRAW_MS`)
- avoid expensive extra buffers in display path

### Q13. Why did encoder direction need tuning?
Physical user expectation was CW as right/down and CCW as left/up. Mapping was adjusted to align with UX.

---

## 6) Calibration and Measurement Questions

### Q14. What is tare?
Tare is baseline offset when no load is present. It removes static bias from raw ADC values.

### Q15. Why is tare saved persistently?
To avoid repeating tare calibration every power cycle and keep baseline consistency.

### Q16. What is scale factor?
Scale factor converts raw delta counts into mass units after tare subtraction.

### Q17. Why multi-point calibration?
Single-point calibration can misrepresent slope across range. Multi-point fit improves overall linear accuracy.

### Q18. What formula do you use for scale factor?
Least-squares slope with fixed tare:
- `raw - tare = scale_factor * base_mass`
- `scale_factor = sum(base_mass * raw_delta) / sum(base_mass^2)`

### Q19. Why convert entered weight into base mass (`g=1`)?
Because display weight should vary by profile gravity, but calibration baseline should remain universal and reusable.

### Q20. What happens if calibration points are poor?
Errors propagate to all measurements. So reference weights and stable capture conditions are critical.

---

## 7) Filtering and Stability Questions

### Q21. Why are raw load cell readings noisy?
Mechanical vibration, ADC noise, microstrain settling, and electrical interference.

### Q22. Which filtering methods are present?
- moving average
- median utility
- EMA for practical runtime smoothing

### Q23. Why EMA for runtime display?
Low CPU cost, smooth output, and faster response tuning through one parameter (`EMA_ALPHA`).

### Q24. How do you classify stable/settling/unstable?
Using spread in recent window:
- small spread -> stable
- medium spread -> settling
- large spread -> unstable

### Q25. What is locked state?
After consecutive stable cycles, displayed value is temporarily frozen for readability and user confidence.

---

## 8) Display and UI Questions

### Q26. Describe the UI layout.
- title/status group
- large weight group
- profile/g info group
- action bar (tare/profile/menu)

### Q27. Why did you create a separate color test script?
To isolate panel color issues independently from main app logic and verify channel/inversion/byte-order correctness.

### Q28. What caused wrong colors during development?
RGB565 byte-order mismatch between framebuffer byte layout and panel expectation.

### Q29. How was memory issue solved?
Removed extra full-frame swap buffer; used in-place byte swap during display transfer.

### Q30. Why wrap menu text?
Small TFT width can clip long labels; wrapping improves readability and usability.

---

## 9) Persistence and Data Integrity Questions

### Q31. What data is persisted?
- `profiles.json`: profiles, active profile, language
- `calibration.json`: tare offset, scale factor, base model metadata

### Q32. Why atomic-like save in profile store?
Using temp file + replace reduces corruption risk if power interruption occurs during write.

### Q33. What happens if file data is invalid?
Data normalization and fallback defaults recover the app to valid state.

---

## 10) Testing and Validation Questions

### Q34. How did you test functionality?
Menu flows, profile CRUD, language switching, calibration completion, startup/ manual tare persistence, and encoder interaction tests.

### Q35. How did you test measurement quality?
Known weight points (e.g., 1.0, 2.5, 5.0 kg), repeatability checks, drift checks, and error logging.

### Q36. What metrics did you track?
- absolute error
- percent error
- repeatability spread
- drift over time
- practical UI responsiveness

### Q37. Why is repeatability important?
A reliable scale must produce near-same value on repeated placement of same weight.

---

## 11) Practical Debug Questions

### Q38. If readings are always 4x, what will you check first?
Correction factor misuse, stale calibration data, and scale-factor derivation path.

### Q39. If encoder feels laggy, what do you tune?
Input-first loop behavior, redraw interval, debounce thresholds, and unnecessary render workload.

### Q40. If no-load drift appears after some minutes?
Inspect mechanical mounting, grounding, cable routing, and re-run tare in stable conditions.

### Q41. If display is blank?
Check SPI pins (SCK/MOSI/CS/DC/RST), power rails, and display init sequence.

---

## 12) Design Trade-Off Questions

### Q42. Why MicroPython instead of C/C++ firmware?
Faster development iteration for student project and easier demonstration of algorithmic/UI changes.

### Q43. What are the trade-offs of full-frame redraw?
Simpler render logic but higher CPU load. Mitigated by redraw throttling.

### Q44. Why not add too many features?
Embedded projects need stable, testable scope. Prioritized reliability and demonstrable correctness.

---

## 13) Ethics, Safety, and Reliability Questions

### Q45. Is this medically certified?
No. It is an educational embedded system and not a certified medical measuring device.

### Q46. Can this be used for legal-for-trade measurement?
No, not without certified hardware calibration and compliance processes.

### Q47. How do you communicate limitations?
By documenting calibration dependence, environmental sensitivity, and intended educational scope.

---

## 14) Future Scope Questions

### Q48. What are your next improvements?
- partial redraw for faster UI
- richer automated tests for state transitions/math
- diagnostics counters and calibration reports
- optional cloud logging/dashboard

### Q49. How can this be made production-grade?
Hardware enclosure refinement, EMI hardening, robust power design, calibration tooling, error logging, and certification pathways.

---

## 15) Rapid-Fire Short Answers (One Line Each)

- Why tare? -> To remove no-load offset bias.
- Why multi-point calibration? -> Better range linearity.
- Why interrupt input? -> Lower latency and missed-event reduction.
- Why state machine? -> Deterministic UI behavior.
- Why persistence? -> No repeated setup after reboot.
- Why profile g-values? -> Simulate weight display under different gravity.
- Why EMA? -> Good smoothness with low CPU cost.
- Why lock stable value? -> Better readability and user trust.
- Why color test script? -> Isolate and verify display color path.
- Why docs and test matrix? -> Reproducible validation and academic clarity.

---

## 16) Questions You Should Ask Back (Shows Maturity)

Use these when professor asks open-ended improvement questions:

1. "Should I optimize for faster response or smoother display first?"
2. "Would you prefer I focus on algorithm validation depth or UI experience in final demo?"
3. "For future scope, should I prioritize test automation or hardware ruggedization?"

These questions show engineering prioritization thinking.

---

## 17) Final 30-Second Closing Statement

"This project demonstrates complete embedded product thinking: sensor interfacing, signal conditioning, user interaction design, deterministic state control, persistence, debugging under constraints, and measurable validation. I focused on making it accurate, usable, and explainable."

