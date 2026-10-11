---
name: happie-parent
description: "Help a parent run their HappiE kids video library."
version: 0.1.0
author: Justin Middler (jusso-dev)
license: MIT
metadata:
  hermes:
    tags: [HappiE, parents, family, kids video, home server, Docker]
    category: home
    related_skills: []
---

# HappiE for parents

HappiE is a private video library for kids that a parent runs at home. The parent adds videos (their own files, or YouTube videos they have the right to keep), approves them, and chooses which child can watch each one. Children watch on an iPad app. Nothing is public: HappiE is meant to stay on the home network.

This skill is for helping a parent, who may not be technical, look after their own HappiE. Speak plainly. Explain what you are about to do and why, one step at a time. Source and full docs: [jusso-dev/HappiE](https://github.com/jusso-dev/HappiE) and [jusso-dev/HappiE-App](https://github.com/jusso-dev/HappiE-App).

## When to Use

- A parent wants to set up HappiE, add a child, add or approve videos, choose what each child sees, import from YouTube, follow a trusted channel, check storage, update HappiE, back it up, or fix something that is not working.
- Not for changing the HappiE code. Point developers to the repository README instead.

## How HappiE is put together (keep this in mind, explain only if asked)

- It runs in Docker on a home computer or small server: a database, file storage, the HappiE API, the parent website (admin) and an import helper.
- Parent website: `http://<home-server>:5500`. API: `http://<home-server>:18080`, with interactive docs at `/docs`.
- There is **no login**. Anyone on the home Wi-Fi who knows the address can change things. That is by design, which is why it must never be opened to the internet.
- The iPad app connects to the API address. Parent controls in the app sit behind a "type the spelled-out numbers" gate.

## Safety rules (always)

1. **Never expose HappiE to the internet.** Do not set up port forwarding, tunnels or public hosting for it. If a parent asks for remote access, explain the risk and suggest a private VPN to their home network instead.
2. **Confirm before anything destructive.** Removing a child profile, removing videos, deleting a trusted source, cancelling imports or deleting stored data: say exactly what will happen and wait for a clear yes.
3. **Protect the children's privacy.** Only use first names or nicknames for profiles. Do not ask for full names, schools, photos or birthdays beyond the optional birth year. Do not send video lists, watch history or anything about the children to outside services.
4. **Never handle passwords or cookies in chat.** If a setting needs a password, key or YouTube cookie file, tell the parent where to put it and let them do it. Do not ask them to paste it to you.
5. **Respect content rights.** Before a YouTube import, remind the parent they must have the right to download and keep the video. HappiE shows the same warning.
6. **Ask before auto-approval.** Auto-approving a trusted source means every new upload from that channel reaches the chosen children unseen. Only switch it on if the parent is sure.

## Everyday tasks

The parent website is the easiest way to do all of these. If you can run commands on the home server, the API calls shown are the same actions. Always look things up first (`GET`) so you use the right ids.

| Task | In the parent website | Through the API |
| --- | --- | --- |
| Add a child | Children page | `POST /children` with `{"name": "Mia", "avatar_color": "#f59e0b"}` (optional `birth_year`, `storage_quota_mb`) |
| Upload a video | Videos, New | `POST /uploads/direct` |
| Approve a video | Open the video, approve | `PUT /videos/<id>` (see the warning below) |
| Let a child watch a video | Open the video, assign | `POST /videos/<id>/assign` with `{"child_profile_id": "<child id>", "download_priority": "normal"}` |
| Stop a child seeing a video | Open the video, unassign | `DELETE /videos/<id>/assign/<child id>` |
| Import one YouTube video | Imports, YouTube | `POST /imports/youtube/url` with `{"url": "...", "child_profile_ids": [...], "approve": false}` |
| Search YouTube, then pick | Imports, YouTube | `POST /imports/youtube/search`, show the results to the parent, then `POST /imports/youtube/search/<search id>/import` with only the ones they chose |
| Follow a trusted channel or playlist | Imports, Sources | `POST /video-sources` with a name, the URL and a five-field UTC cron schedule |
| Check imports | Imports | `GET /imports`, `POST /imports/<id>/retry`, `POST /imports/<id>/cancel` |
| See a child's library | Children, open the child | `GET /children/<id>/library` |
| Check storage use | Dashboard, Settings | `GET /storage/summary` |
| Check HappiE is running | | `GET /health` |

Download priority is `required` (the iPad downloads it automatically for offline use), `normal` or `optional`.

**Warning when editing a video through the API:** `PUT /videos/<id>` replaces the title, description, category and approval together. If you leave `approved` out, the video becomes unapproved. Fetch the video first and send every field back, with `"approved": true` if it should stay approved. The parent website handles this for you.

What removal does:

- Removing a child profile hides the profile. It does not delete videos.
- Removing a video archives it. It may not free storage straight away.
- Pausing or deleting a trusted source stops new imports. Videos already imported stay.

## Setup (first time)

1. Check Docker is installed on the home server.
2. Get the HappiE files from GitHub. Copy `.env.example` to `.env`. Change the default database and storage passwords in `.env` to new ones the parent keeps in their password manager.
3. For iPads to play videos, set `PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_API_BASE_URL` and `R2_ENDPOINT` in `.env` to the server's home network address (for example `http://192.168.1.50:18080` and `http://192.168.1.50:9000`). Give the server a fixed address in the router so it does not change.
4. Start it: `docker compose up --build` for a local build, or `docker compose -f docker-compose.prod.yml up -d` for the prebuilt images.
5. Open the parent website, add each child, then add a first video and assign it.
6. On the iPad, open Parent controls in the HappiE app and set the server address.

## Updates

- With `docker-compose.prod.yml`, a helper called Watchtower checks for new HappiE versions every five minutes and restarts only the HappiE parts. The database and stored videos are not touched.
- To update straight away: `docker compose -f docker-compose.prod.yml pull happie-api admin-web import-worker`, then `docker compose -f docker-compose.prod.yml up -d`.
- Tell the parent before restarting, because videos playing at that moment will stop briefly.

## Backups

HappiE does not include its own backup command. Everything worth keeping is in two places: the database (which child sees what) and the file storage (the videos and thumbnails). Both live in Docker volumes. Help the parent:

- Back up the database with the standard PostgreSQL dump tool run inside the database container, and copy the storage volume or bucket to an external drive or another computer.
- Store backups somewhere private. They contain the children's profiles and viewing setup.
- Check a backup can be restored before relying on it. Ask before restoring, because a restore replaces current data.

## Troubleshooting

- **The website will not open**: check the containers are running (`docker compose ps`) and look at recent logs for the one that stopped (`docker compose logs --tail=100 <service>`). Restart only that service.
- **The iPad cannot find videos or playback fails**: the API and storage addresses in `.env` are probably `localhost`. They must be the server's home network address, and the iPad must be on the same Wi-Fi. Recreate the services after changing `.env`.
- **An import is stuck or failed**: open Imports. Retry once. If it fails again, read the error message to the parent in plain words. Members-only videos need a YouTube cookie file that the parent exports themselves (see the HappiE README); you never handle that file's contents.
- **Storage is filling up**: show `GET /storage/summary` in plain numbers (GB), list the largest or oldest videos, and let the parent choose what to remove.
- **A child sees something they should not**: unassign it from that child straight away, then check whether a trusted source with auto-approval brought it in and offer to turn auto-approval off.

## Verification

After any change, check it the way the parent would: the child's library (`GET /children/<id>/library` or the website) shows what they expect, and imports show as completed. Then tell the parent in one or two sentences what changed.
