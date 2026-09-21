# Image-provider comparison — September 17, 2026

## Discontinued by the user

The user first narrowed the comparison to Gemini, then rejected the result and
requested built-in imagegen only, technical integration before sprite polish.
Do not make further external generation requests. Two requests are retained:
`round1-pro` generated a1264x848 JPEG with excessive fine detail and unwanted
grid lines; `round1-flash` returned STOP with an empty text part and no image.
Private exact requests/responses/usage are under build/art/provider-comparison/
gemini/. No automatic retry or reference-guided request followed. The generated
reference board has unaccepted palette/crop issues. No council reviewed these.

The existing billed Gemini project was used for those two requests; no user-set
spending cap was provided. The older no-inference/pending-cap statements below
describe the preceding setup checkpoint, not current activity. No credits were
purchased, billing changed or fal API key created. The local credential helper
is stopped; encrypted credentials remain private and unused.

The user rejected the current designs, especially their conversions, and explicitly requested a wide variety of image-generation sources, browser-assisted API setup, and a council to compare and rank results. The subsequent correction specifies API access, not generation in consumer chat websites. This supersedes the built-in-only method for this comparison. No current draft is accepted.

## Access state

- Google AI Studio: existing project/API key reused. Key saved under `.local/image-api-secrets.json`, encrypted with Windows DPAPI to the current account. Neither raw key nor authenticated requests are logged. `scripts/check-image-api-access.py` successfully made a read-only model-list request; evidence `build/art/provider-comparison/gemini-access.json`. No paid inference was made.
- Live Gemini catalog includes `gemini-3-pro-image`, `gemini-3.1-flash-image`, `gemini-3.1-flash-lite-image`, their available preview variants and legacy `gemini-2.5-flash-image`. Use returned canonical IDs, not remembered model availability.
- Google shows a postpay-to-prepay billing notice. Billing is unchanged; authentication success does not establish paid image generation success.
- fal account created through the user-approved Google sign-in and terms acceptance. API-only key description `FFTA art comparison` is prepared; creation awaits the specific access-credential confirmation. API scope cannot manage keys, billing, usage or compute. Current credit balance is zero.
- API spending-cap question remains pending. Do not infer a budget from a preselected option, account creation, a billed Google project or elapsed time. Do not purchase credits or run paid inference without it.

## Comparison procedure

1. Use a shared brief and authenticated native style references. Keep original characters as proportion/format references only. All new designs must be original.
2. First compare the same Human Samurai, Nu Mou Geomancer and Moogle Chemist front/back sheet. These stress human costume identity, Nu Mou anatomy and Moogle face/palette readability. Use all five races in the follow-up and all ten classes for final consistency acceptance.
3. Ask for deliberate native-sized pixel clusters, compact bodies, dark connected outlines and clear face/hand/weapon shapes. The previous approach of detailed illustrations compressed to a small footprint is rejected. Preserve each provider's original output and exact request.
4. Use the same logical 32x32 cells, facing, equipment-side map and limited-palette target. Record the provider's actual resolution and deviations. Do not mislabel an illustration as a native sprite because it can be resized.
5. Compare source images, honest native-size previews and magnified nearest-pixel previews. Conversion must be documented and identical where applicable; keep conversion failures separate from source-design failures. No code-drawn or manually patched artwork.
6. Give blinded candidate IDs to the user-authorized council. Rank FFTA fidelity/racial anatomy, native readability, class identity, front/back equipment continuity and repeat-generation consistency. Require concrete one-based row/column findings, not preference-only scores.
7. A top-ranked result is not automatically accepted. Revise the leaders using their model/reference controls, then verify a repeated pose, opposite view and real alternating gait before extending all animations. Retain losers and limitations.
8. Only after consistent visual acceptance continue native imports. G01-G04 remain open; model comparison does not replace native decoder, palette, OAM, consumer, animation or delivery acceptance.

## Candidate model families and official API documentation

- Gemini Pro and Flash Image: https://ai.google.dev/gemini-api/docs/image-generation
- FLUX.2 Pro: https://fal.ai/models/fal-ai/flux-2-pro/api
- Ideogram 4: https://fal.ai/models/ideogram/v4/api
- Seedream 5.0 Pro: https://fal.ai/models/bytedance/seedream/v5/pro/text-to-image/api
- Qwen Image 3: https://fal.ai/models/alibaba/qwen-image-3/text-to-image/api

These are candidates, not measured rankings. Provider access and actual generation must be verified before claiming coverage. Pricing must be checked against the requested image size and tier before submissions.

## Credential handling

`scripts/image_api_credentials.py --serve 8771` starts a loopback-only, single-purpose setup form with a random route and same-origin POST check. The form saves DPAPI-encrypted values only. It cannot expose stored keys. Browser credential dialogs are inspected without emitting secrets. Native browser copy did not populate the automation clipboard; the existing Gemini key was transferred directly from its visible dialog to the local password form without printing it. Stop the helper after setup. Runtime API clients decrypt only the named provider key and send it only to that provider's authenticated API endpoint.
