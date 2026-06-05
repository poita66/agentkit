# Session: Frontend: Prominent final answer display

**Session ID:** ses_16a1ba2e5ffeVOFW96qkRLJexi

**Agent:** build

**Model:** llama/default

**Messages:** 13

---

## User (1)

Ensure the following is true for the frontend: Show the final answer prominently. When the run finishes successfully, the agent's final response should be the most visible thing on the screen, not buried at the end of the timeline.

---

## Assistant (2)

Let me read the relevant files to understand the current layout.

---

## Assistant (3)

Let me check the backend API types and the formatOutcome utility to understand where the final answer lives.

---

## Assistant (4)

I can see the issue. The final answer is currently buried as the last `StepCard` in the timeline. The backend stores it as `{"answer": "..."}` in the last step's result, but `formatStep.ts` reads `step.result?.data` (wrong key). I need to:

1. Extract the final answer and show it prominently at the top
2. Fix the `result.data` → `result.answer` bug
3. Make it the most visible element on screen

---

## Assistant (5)

Now I'll make the changes. I need to:
1. Fix `formatStep.ts` to read `result.answer` instead of `result.data`
2. Add a prominent final answer display at the top of `RunDetail.tsx`

---

## Assistant (6)

Now let me update `RunDetail.tsx` to show the final answer prominently at the top:

---

## Assistant (7)

Now add the prominent styling for the final answer card:

---

## Assistant (8)

Let me verify the final state of the file:

---

## Assistant (9)

I should also fix the auto-scroll behavior — when the final answer step arrives, the user should stay at the top to see the prominent answer card, not be scrolled to the bottom of the timeline:

---

## Assistant (10)

Let me verify the frontend builds:

---

## Assistant (11)

Done. Here's what changed:

**`frontend/src/components/RunDetail.tsx`**:
- Extracts the final answer from the step where `tool_name === null`
- Shows a prominent green-bordered "Answer" card at the top of the page (after the goal header) when the run succeeds
- Stops auto-scrolling to the bottom when the final answer step arrives, so the user sees the answer at the top

**`frontend/src/utils/formatStep.ts`**:
- Fixed `step.result?.data` → `step.result?.answer` to match the backend's actual response format

The final answer now appears in a large card (1.25rem text, green background, 2px green border, shadow) right after the goal header — the most visible element on the page.

---

## User (12)

commit

---

## Assistant (13)

Done. Committed as `153fec9`.

---

