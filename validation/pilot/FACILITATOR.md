# Facilitator guide for the synthetic pilot

Ask five independent people outside the implementation team to use the participant ZIP. Use participant IDs P01 through P05. Collect only consented, anonymous notes. Store the completed scoring sheet locally. Use the same first instructions for every participant.

## Prepare the participant ZIP

Build the archives using the offline release verifier. Use new paths in an owner-controlled directory. The builder checks the wheel hash against evidence from that run.

```sh
pilot_dir="$(mktemp -d)"
pilot_dir="$(cd "$pilot_dir" && pwd -P)"
python3 scripts/verify_release.py --out "$pilot_dir/verification.json" \
  --artifacts "$pilot_dir/artifacts"
python3 validation/pilot/build_kit.py \
  --wheel "$pilot_dir/artifacts/mindtunnel-0.0.1-py3-none-any.whl" \
  --verification "$pilot_dir/verification.json" --out "$pilot_dir/participant-kit.zip"
```

Give each participant only `participant-kit.zip`. It includes setup steps, a wheel, synthetic fixtures and the questionnaire. Keep this guide, scoring sheet and verification evidence with the facilitator.

## Run a session

1. Start the clock when the participant opens the kit's README. Record their OS, Python version, time to a correct count report and setup outcome. Record elapsed time and blockers for incomplete sessions.
2. Ask participants to work through the instructions, then complete the questionnaire in their own words. Let them attempt the exercise and rejection check before helping. If they request help, record the time and hint. Distinguish setup and command help from hints that explain the planning boundary.
3. Record answers to questionnaire items 4 and 5 before discussing them. Score understanding using the rubric below. Give any remaining help and share the intended workflow after scoring.
4. Record one anonymous observation about confusing steps or obstacles. Retain only consented paraphrases. Keep private notes, account details, terminal transcripts and machine paths out of the sheet.

## Score the outcomes

The count report should show groups east 2, north 1 and west 2. The exercise result should show the ungrouped sum 17. The extra action should yield exit status 2 and `Rejected: plan_keys`, with no `results/rejected.json`.

Mark the boundary explanation **unaided** if the participant identifies all three points without any hint that supplies one of them.

- The proposed planner receives only the reviewed public question and alias/type contract. The participant can inspect the exact request before transfer.
- The CSV rows and the local mapping are handled locally, and local execution produces the result.
- Results and errors stay local unless the user explicitly shares them. The CLI provides no automatic feedback to the planner.

Mark an otherwise correct explanation after a boundary hint as **assisted**. Mark an incomplete or incorrect explanation as **incomplete**. Record missing responses as **unobserved** and preserve all five participants in the denominator. Use the [standardized scoring sheet](score-sheet.csv).

The acceptance criterion is five outside attempts and at least three of five **unaided** explanations. Report setup completions, grouped and exercise accuracy, rejection observations, total interventions, and time to first correct report among people who reach it. Report the number reaching that result under five minutes. These measure human usability. The separate scripted demo gate requires under 60 seconds excluding any model latency.
