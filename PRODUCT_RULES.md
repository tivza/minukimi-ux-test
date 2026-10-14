# MINUKIMI product rules

## Main profile photo — hard face gate

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
