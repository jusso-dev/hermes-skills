---
name: servicesnap
description: "Work on the ServiceSnap vehicle logbook apps."
version: 0.1.0
author: Justin Middler (jusso-dev)
license: MIT
metadata:
  hermes:
    tags: [ServiceSnap, iOS, Android, Firebase, SwiftUI, Jetpack Compose]
    category: products
    related_skills: []
---

# ServiceSnap

ServiceSnap is a vehicle maintenance logbook for Australian owners of cars, motorcycles, utes and machines. Owners record services, fuel, parts, registration, reminders, gear and receipts for each vehicle, and can share a vehicle with another person as a viewer or an editor. There is a native iOS app and a native Android app. Both talk to one shared Firebase backend.

The source repositories are private. This skill covers architecture and developer workflow only. It does not contain, and you must not add to it, project identifiers, signing details, storage endpoints, bucket names, keys or user data.

## When to Use

- The user asks you to change, debug, test or release ServiceSnap on iOS, Android or the Firebase backend.
- The user asks how sharing, reminders, receipt uploads or usage limits work in ServiceSnap.
- Not for general Firebase questions unrelated to ServiceSnap, and not for answering end-user support questions about someone's own vehicle data.

## Repository map

Ask the user for access if you cannot see these repositories. They are private.

| Repository | What it holds |
| --- | --- |
| `ServiceSnap-IOS` | SwiftUI app, a WidgetKit garage widget, the shared Firebase backend (`functions/`, `firestore.rules`, `firestore.indexes.json`, `firebase.json`) and iOS fastlane |
| `ServiceSnap-Android` | Kotlin and Jetpack Compose app, a Glance widget, Android fastlane |
| `ServiceSnap-Policies` | Public privacy policy and terms pages (static HTML) |

The backend lives in the iOS repository but serves both apps. Treat a change there as a change to both clients.

### iOS (`ServiceSnap-IOS`)

- `project.yml`: XcodeGen spec. The `.xcodeproj` is generated. Never hand-edit `ServiceSnap.xcodeproj`; edit `project.yml` and run `xcodegen generate`.
- `ServiceSnap/Models`: `Vehicle`, `ServiceRecord`, `FuelRecord`, `PartRecord`, `GearItem`, `ServiceReminder`, `RegoReminder`, `Invitation`.
- `ServiceSnap/ViewModels`: one view model per record type, plus `ShareViewModel` and `VehicleViewModel`.
- `ServiceSnap/Views`: SwiftUI screens (`DashboardView`, `VehicleDetailView`, `Add*View`, `ShareVehicleView`, `InvitationsView`, `ExportServiceHistoryView`, `SettingsView`).
- `ServiceSnap/Services`: auth (`AuthenticationManager`, `AuthTokenManager`), App Check, `ImageUploadService`, `NotificationManager`, `ServiceHistoryPDFGenerator`, widget snapshot and background refresh.
- `ServiceSnapWidget` and `Shared`: the widget target and the snapshot type it shares with the app.
- `ServiceSnapTests`, `SnapshotTest`: unit tests and the UI-test target that drives App Store screenshots.
- `functions/src`: Cloud Functions in TypeScript (`index.ts`, `sharing.ts`, `security.ts`, `account-deletion.ts`, `attachment-metadata.ts`, `r2-deletion.ts`). Tests are in `functions/test`.
- `docs/usage-limits.md`: rate limits enforced by the backend.

### Android (`ServiceSnap-Android`)

- Gradle Kotlin DSL with a version catalogue in `gradle/libs.versions.toml`. Compose, Material 3, Navigation Compose, Coil, DataStore, Glance and the Firebase BoM (Auth, Firestore, Functions, Messaging).
- `app/src/main/java/.../ServiceSnap/`: `models`, `viewmodels`, `screens`, `navigation`, `services`, `ui/theme`, `ui/components`, `widget`.
- `app/src/test` and `app/src/androidTest`: unit tests and instrumented screen tests.
- `PRODUCT.md` and `DESIGN.md` in each repo describe the product and design rules. Read them before UI work.

## Architecture

- **Auth**: Firebase Authentication. App Check guards the callable functions.
- **Data**: Cloud Firestore. Top-level collections: `users` (with a `pushTokens` subcollection), `vehicles`, `services`, `fuelRecords`, `reminders`, `regoReminders`, `gearItems`, `parts`, `invitations` and `system`. Rate-limit counters live in a server-only collection that clients cannot read.
- **Ownership model**: every record is keyed to the vehicle owner's uid, even when an editor creates it. Access is derived from the parent vehicle: `sharedUids` can read, `editorUids` can write. `firestore.rules` enforces this with helpers such as `canReadVehicle`, `canWriteVehicle` and `keyedToOwner`.
- **Sharing**: owners invite by callable function. An invitation must be explicitly accepted before access is granted. Only owners can manage invitations, revoke access, change ownership-level settings or delete the vehicle. Invitations are written only by functions, never by clients.
- **Attachments**: receipts and photos go to S3-compatible object storage through short-lived presigned URLs issued by functions. Clients never hold storage credentials. Limits are 10 MiB per file and five attachments per record. Attachment metadata cannot be set by a client on create.
- **Reminders**: scheduled functions check service, registration and gear reminders and send push notifications through Firebase Cloud Messaging.
- **Account deletion**: a callable function removes the user's Firestore data and stored objects.
- **Usage limits**: callable functions enforce per-user and project-wide rolling windows and return `resource-exhausted` with `retryAfterSeconds` and `resetsAtMs`. See `docs/usage-limits.md` before changing any limit.

## Procedure

1. Read `PRODUCT.md`, `DESIGN.md` and, for backend work, `firestore.rules` and `docs/usage-limits.md` before editing.
2. Decide which surfaces the change touches. A data-model change usually needs the iOS model, the Android model, the rules and sometimes a function. Keep the Firestore contract identical on both platforms.
3. iOS:
   - Install `xcodegen` and `fastlane`.
   - Get the Firebase client config file for iOS from the project owner and place it where `project.yml` expects it. It is gitignored. Never commit it.
   - `xcodegen generate`, then build in Xcode or run `fastlane tests` for the unit tests.
4. Android:
   - Use the Gradle wrapper: `./gradlew assembleDebug` and `./gradlew test`.
   - The app needs the Firebase client config for Android. Get it from the project owner rather than creating a new Firebase project.
5. Backend (`functions/`, Node 22):
   - `npm ci`, then `npm run lint`, `npm run build` and `npm test`.
   - `npm test` runs contract and security tests, then rules and function tests inside the Firebase emulators. Install the Firebase CLI first.
   - Add or update a rules test in `functions/test/firestore.rules.test.js` for any change to `firestore.rules`.
6. Run both apps against the change before calling it done when the backend contract moved.

## Releases

- iOS lanes: `fastlane certs`, `tests`, `screenshots`, `beta`, `metadata`, `release`. Every lane regenerates the project with XcodeGen. Nothing is auto-submitted for review.
- Android lanes include `build_release`, `internal`, `beta`, `production` and screenshot lanes.
- Signing material, store API keys and the Firebase config are supplied by the owner's machine or CI secrets. Do not run a release lane, deploy functions (`npm run deploy`) or deploy rules unless the user asks for that exact step.

## Pitfalls

- Editing the generated Xcode project directly. The next `xcodegen generate` throws the change away.
- Writing a record keyed to the editor's uid instead of the owner's. The rules reject it, and dashboard queries that filter by owner uid stop finding it.
- Adding a list query that relies on `canReadVehicle()` without pinning `vehicleId`. Firestore rejects it because the rule needs a `get()` on an unbound id.
- Letting a client write attachment metadata or invitations directly. Those paths are function-only on purpose.
- Raising a usage limit without checking real usage. The limits are cost-safety defaults.
- Changing behaviour on one platform only. Sharing and reminders must behave the same on iOS and Android.

## Safety rules

- Never commit or paste Firebase config files, store API keys, signing certificates, match passphrases, storage endpoints or credentials. They are gitignored or held in CI secrets.
- Never read, export or copy production user data, vehicle records or receipts. Use the Firebase emulators and fictional data.
- Do not deploy functions, rules or app builds without an explicit request.
- This skill is public. If you improve it, keep project identifiers, internal URLs and customer details out.

## Verification

- iOS unit tests pass (`fastlane tests` or Xcode).
- Android `./gradlew test` passes and the debug build assembles.
- `functions` lint, build and `npm test` pass, including the emulator suites.
- Rules changes have a matching rules test.
