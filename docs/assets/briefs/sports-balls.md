# Sports balls: brief and audit

Status: first pass for review, written from the generator (`art/scripts/sports.py`) and `out/meta`. **The real-world numbers below are from memory of the governing rules and are not yet checked against the sources**; step 2 of the `asset-brief` skill says to do that before building. US reference.

## What exists (9, one of each, no variants)

| Model | Radius in the script | Real size (to verify) | Detail kept | Verdict |
|---|---|---|---|---|
| Basketball | 0.121 m | size 7: about 0.24 m across; 6, 5, 3 are smaller | three black belts | Size fine for 7. Needs the size classes and the real channel layout (one belt each way plus two curved side channels) |
| Soccerball | 0.110 m | size 5: about 0.22 m | 12 black pentagons on white | Right layout. Needs sizes 4 and 3, a futsal ball, a coloured training ball |
| Baseball | 0.037 m | about 0.074 m | red seam | Fine. The seam is a ring; the real one is two curved stitched lobes (detail pass only) |
| TennisBall | 0.033 m | about 0.066 m | white seam | Fine |
| Football (American) | 0.28 m long | about 0.28 m long, 0.17 m wide | laces, two white stripes | Fine. A youth size is missing |
| Volleyball | 0.105 m | about 0.21 m | yellow with blue belts | Reads as a volleyball. The real ball has 18 panels in 6 groups of 3; a white beach version is missing |
| GolfBall | 0.0214 m | about 0.0427 m | none (8 sides, 76 triangles) | **Needs detail**: no dimples, visibly an octagon. Fake the dimples with a spotted palette ring or raise the sides |
| BowlingBall | 0.108 m | about 0.218 m | 3 holes, violet | Fine shape. Only one colour; holes are flat patches |
| HockeyPuck | 0.038 m radius, 0.0254 m high | 0.076 m across, 0.0254 m high | none | Size right. Missing the bevelled edge and the knurled band |

## Missing family members (US first)

Softball, pickleball, lacrosse ball, pool/billiard set (cue ball, 8-ball, numbered balls), table-tennis ball, dodgeball, playground / kickball rubber ball, beach ball, exercise (stability) ball, medicine ball, bocce set, croquet ball, shuttlecock (badminton), cricket ball, rugby ball, Australian-rules ball, handball, water-polo ball, field-hockey ball.

## Variants to decide

- **Size classes** as scale variants of one script: basketball 7 / 6 / 5 / 3, soccer 5 / 4 / 3, football adult / youth.
- **Colour themes** through `props_lib.THEME`: bowling (several colours), volleyball (white beach), basketball (indoor leather vs outdoor rubber), soccer (coloured training).
- **Condition**: flat / worn / dirty, if the game uses them (open question).

## Proposed batches

1. **Fix**: golf ball dimples, hockey puck edge, basketball channels, bowling ball colours. No id changes.
2. **Size and colour variants** of the existing nine.
3. **New balls**: softball, pickleball, lacrosse, ping-pong, dodgeball, playground ball, beach ball, exercise ball, medicine ball, pool set.
4. **Later**: the non-US balls (cricket, rugby, handball, water polo, Australian rules) after #346 is decided.

## Open questions for the owner

- Do size classes matter in the game, or is one regulation size per ball enough?
- Is a flat or worn ball needed?
- Are the non-US balls wanted at all (the reference region is US)?
