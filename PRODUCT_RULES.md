# MINUKIMI product rules

## Main profile photo - hard face gate

The first / main profile photo must show the profile owner clearly. This is an enforced upload rule, not a suggestion.

Reject the main photo automatically when:

- no human face is detected;
- more than one face is detected;
- the face is too small to identify comfortably in the discovery card;
- the face is substantially hidden, turned away, cropped out, or too dark to read;
- the upload is primarily an object, pet, scenery, vehicle, food, laptop, furniture, artwork, meme, or other non-face image.

Accept only when one clear face is present and can be placed inside the discovery-card safe zone.

The upload UI must show a simple face/shoulders placement guide and live card preview. The user may reposition and zoom the photo, but repositioning must not bypass the face gate.

Secondary profile photos may later allow pets, travel, hobbies, objects, etc.; the hard face requirement applies to the main discovery photo.

Implementation target for the web/PWA onboarding: client-side face detection with a server-side moderation/validation fallback so the rule works consistently across browsers.

## Signature heart interaction

The two animated lines are the central MINUKIMI interaction and a core part of the brand, not decoration.

At rest:

- there are exactly two open line halves;
- each line is visibly one half of the same heart and has a long outward tail;
- the two halves are separated at both the upper cleft and lower point;
- no extra heart outline, loop, node, circle, handle mark, or decorative micro-line may be used to explain the shape.

Positive choice:

- the user pulls either half toward the other;
- the other half responds with magnetic attraction;
- both existing lines physically meet and become one complete heart;
- the connection moment receives a refined glow, small spark event, subtle haptic feedback, and a clearly visible `I see it.` confirmation.

Negative choice:

- the user flicks either half away;
- the selected half leaves the card cleanly;
- the interaction must not reward rejection more strongly than connection.

The onboarding animation must use the exact same heart geometry as the live discovery card so a user can understand the gesture without reading detailed instructions.

Visual direction: elegant, emotional, contemporary, premium, and restrained. Avoid cartoon loops, figure-eight shapes, childish effects, or generic swipe-app language.
