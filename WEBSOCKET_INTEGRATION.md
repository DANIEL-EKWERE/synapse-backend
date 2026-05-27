# SYNAPSE — WebSocket / Django Channels Integration

## Stack
- **Backend**: Django 5 + Django Channels 4 + Daphne (ASGI)
- **Frontend**: Next.js 14 (App Router) + custom WS hooks
- **Auth**: HS256 JWT — issued by Django on login, passed as `?token=<jwt>` on WS handshake and `Authorization: Bearer` on HTTP
- **Channel layer**: Redis (`channels-redis`)
- **No Supabase** — all data flows through the Django REST API

## Architecture

```
Next.js (App Router)
  lib/api.ts              → HTTP REST  → Django DRF  (port 8000)
  hooks/use-meeting-socket   → ws://…/ws/meetings/<uuid>/?token=
  hooks/use-webinar-socket   → ws://…/ws/webinars/<uuid>/?token=
  hooks/use-classroom-socket → ws://…/ws/classrooms/<uuid>/?token=
  hooks/use-coaching-socket  → ws://…/ws/coaching/<uuid>/?token=
                                         ↓
                              Django Channels consumers
                              (JWTAuthMiddleware → scope['user'])
                                         ↓
                              Redis channel layer (group broadcast)
```

## Running

```bash
# 1. Start Redis
redis-server

# 2. Backend — serves both HTTP and WS via Daphne
cd SYNAPSE_backend
pip install -r requirements.txt
cp .env.example .env        # fill in JWT_SECRET etc.
python manage.py migrate
daphne -b 0.0.0.0 -p 8000 SYNAPSE.asgi:application

# 3. Celery worker (AI tasks)
celery -A SYNAPSE worker -l info

# 4. Frontend
cd SYNAPSE_frontend
npm install
# .env already has NEXT_PUBLIC_API_URL and NEXT_PUBLIC_WS_URL
npm run dev
```

## Auth flow
1. User POSTs to `/api/users/login/` → receives `{ token: "..." }`
2. Frontend stores token in `localStorage` via `AuthContext`
3. All `api.ts` calls include `Authorization: Bearer <token>`
4. WS hooks append `?token=<token>` to the WebSocket URL
5. `JWTAuthMiddleware` decodes the token and sets `scope['user']`

## REST endpoints added

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/users/register/` | Create account, returns JWT |
| POST | `/api/users/login/`    | Authenticate, returns JWT |
| GET/PATCH | `/api/users/me/` | Get/update own profile |
| GET | `/api/meetings/` | List user's meetings |
| POST | `/api/meetings/` | Create meeting |
| GET/PATCH | `/api/meetings/<uuid>/` | Meeting detail |
| GET | `/api/meetings/<uuid>/participants/` | Participants list |
| POST | `/api/meetings/<uuid>/join/` | Join meeting |
| POST | `/api/meetings/<uuid>/leave/` | Leave meeting |
| POST | `/api/meetings/<uuid>/token/` | Get LiveKit token |

## WebSocket event reference

### Meetings (`/ws/meetings/<uuid>/`)
| client → server | `reaction`      | `{ emoji, x, y }` |
| client → server | `hand_raise`    | `{ raised: bool }` |
| client → server | `media_status`  | `{ muted, camera_off }` |
| client → server | `chat_message`  | `{ text }` |
| client → server | `moderation`    | `{ action, target_user_id }` |
| server → client | any above       | `+ user_id, user_name` |
| server → client | `participant_joined` / `participant_left` | `{ user_id }` |

### Webinars (`/ws/webinars/<uuid>/`)
| `question_submit` → `question_submitted` | Persisted to DB |
| `question_upvote` → `question_upvoted`   | DB increment    |
| `poll_vote`       → `poll_results`       | DB tally        |
| `attendee_delta`                         | ±1 on connect/disconnect |

### Classrooms (`/ws/classrooms/<uuid>/`)
| `attendance_mark` → `attendance_updated` | Persisted to DB |
| `hand_raise` / `quiz_answer` / `teacher_broadcast` / `assignment_notify` |

### Coaching (`/ws/coaching/<uuid>/`)
| `session_status` → DB update | `note_update` / `timer_sync` sync to both parties |
| `action_item_add` → appended to session notes |
