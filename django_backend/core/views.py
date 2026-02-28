import json
from datetime import datetime

from django.contrib.auth.hashers import check_password, make_password
from django.core import signing
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import (
    AdminAccount,
    Category,
    Event,
    EventImage,
    EventSession,
    OrganizerAccount,
    OrganizerDetails,
    OrganizerProfile,
    TicketType,
    UserAccount,
    Venue,
)

AUTH_SALT = "it_cons_auth"
TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7


def _issue_token(payload):
    return signing.dumps(payload, salt=AUTH_SALT)


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _get_bearer_token(request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header[7:].strip()


def _resolve_account(login):
    admin = AdminAccount.objects.filter(email__iexact=login).first()
    if admin:
        return {
            "role": "admin",
            "id": admin.admin_id,
            "login": admin.email,
            "password_hash": admin.password_hash,
            "status": admin.status,
        }

    organizer = OrganizerAccount.objects.filter(
        Q(email__iexact=login) | Q(phone=login)
    ).first()
    if organizer:
        return {
            "role": "organizer",
            "id": organizer.organizer_account_id,
            "login": organizer.email or organizer.phone or "",
            "password_hash": organizer.password_hash,
            "status": organizer.status,
        }

    user = UserAccount.objects.filter(Q(email__iexact=login) | Q(phone=login)).first()
    if user:
        return {
            "role": "user",
            "id": user.user_id,
            "login": user.email or user.phone or "",
            "password_hash": user.password_hash,
            "status": user.status,
        }

    return None


def _parse_token_from_request(request):
    token = _get_bearer_token(request)
    if not token:
        return None
    try:
        return signing.loads(token, salt=AUTH_SALT, max_age=TOKEN_MAX_AGE_SECONDS)
    except signing.BadSignature:
        return None
    except signing.SignatureExpired:
        return None


def _require_admin_token(request):
    token_payload = _parse_token_from_request(request)
    if not token_payload:
        return None, JsonResponse({"error": "Unauthorized"}, status=401)
    if token_payload.get("role") != "admin":
        return None, JsonResponse({"error": "Forbidden"}, status=403)

    admin = AdminAccount.objects.filter(admin_id=token_payload.get("id")).first()
    if not admin:
        return None, JsonResponse({"error": "Admin account not found"}, status=404)
    return token_payload, None


def _require_role_token(request, role):
    token_payload = _parse_token_from_request(request)
    if not token_payload:
        return None, JsonResponse({"error": "Unauthorized"}, status=401)
    if token_payload.get("role") != role:
        return None, JsonResponse({"error": "Forbidden"}, status=403)
    return token_payload, None


def _organizer_profile_payload(profile):
    return {
        "display_name": profile.display_name,
        "phone": profile.phone,
        "telegram": profile.telegram,
        "whatsapp": profile.whatsapp,
        "website_url": profile.website_url,
        "address_text": profile.address_text,
        "contact_person": profile.contact_person,
        "about_text": profile.about_text,
    }


def _organizer_details_payload(details):
    if not details:
        return {
            "short_legal_name": "",
            "full_legal_name": "",
            "legal_address": "",
            "inn": "",
            "ogrn": "",
            "kpp": "",
            "org_type": OrganizerDetails.ORG_TYPE_LEGAL_ENTITY,
            "registration_date": None,
            "head_full_name": "",
            "head_position": "",
            "okved": "",
            "okopf": "",
            "opf_name": "",
        }

    return {
        "short_legal_name": details.short_legal_name,
        "full_legal_name": details.full_legal_name,
        "legal_address": details.legal_address,
        "inn": details.inn,
        "ogrn": details.ogrn,
        "kpp": details.kpp,
        "org_type": details.org_type,
        "registration_date": details.registration_date.isoformat()
        if details.registration_date
        else None,
        "head_full_name": details.head_full_name,
        "head_position": details.head_position,
        "okved": details.okved,
        "okopf": details.okopf,
        "opf_name": details.opf_name,
    }


@require_GET
def health(request):
    return JsonResponse({"status": "ok"})


@require_GET
def public_events(request):
    now = timezone.now()
    events = (
        Event.objects.all()
        .select_related("category", "venue")
        .prefetch_related("sessions__ticket_types")
        .order_by("event_id")
    )
    payload = []
    for event in events:
        all_sessions = list(event.sessions.all())
        future_sessions = [s for s in all_sessions if s.starts_at >= now]

        # Hide only events that have sessions and all of them are in the past.
        if all_sessions and not future_sessions:
            continue

        first_session = None
        if future_sessions:
            future_sessions.sort(key=lambda x: x.starts_at)
            first_session = future_sessions[0]

        prices = []
        for session in future_sessions:
            for ticket in session.ticket_types.all():
                prices.append(ticket.price)
        min_price = min(prices) if prices else None

        payload.append(
            {
                "event_id": event.event_id,
                "title": event.title,
                "description": event.description or "",
                "status": event.status,
                "category": event.category.name if event.category else None,
                "venue_name": event.venue.name if event.venue else None,
                "venue_city": event.venue.city if event.venue else None,
                "venue_address": event.venue.address if event.venue else None,
                "starts_at": first_session.starts_at.isoformat() if first_session else None,
                "cover_image_url": _event_cover_url(request, event),
                "min_price": str(min_price) if min_price is not None else None,
            }
        )
    return JsonResponse({"events": payload})


@csrf_exempt
@require_POST
def login_view(request):
    payload = _parse_json_body(request)
    if not payload:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    login = (payload.get("login") or "").strip()
    password = payload.get("password") or ""
    if not login or not password:
        return JsonResponse({"error": "login and password are required"}, status=400)

    account = _resolve_account(login)
    if not account:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    if account["status"] != "active":
        return JsonResponse({"error": "Account is blocked"}, status=403)

    if not check_password(password, account["password_hash"]):
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    token_payload = {
        "role": account["role"],
        "id": account["id"],
        "login": account["login"],
    }
    token = _issue_token(token_payload)

    return JsonResponse(
        {
            "token": token,
            "user": token_payload,
        }
    )


@require_GET
def admin_me(request):
    token_payload, err = _require_admin_token(request)
    if err:
        return err
    admin = AdminAccount.objects.filter(admin_id=token_payload.get("id")).first()

    return JsonResponse(
        {
            "admin_id": admin.admin_id,
            "login": admin.email,
            "role": "admin",
            "status": admin.status,
            "created_at": admin.created_at.isoformat() if admin.created_at else None,
        }
    )


@require_GET
def auth_me(request):
    token_payload = _parse_token_from_request(request)
    if not token_payload:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    role = token_payload.get("role")
    account_id = token_payload.get("id")

    if role == "admin":
        admin = AdminAccount.objects.filter(admin_id=account_id).first()
        if not admin:
            return JsonResponse({"error": "Account not found"}, status=404)
        return JsonResponse(
            {
                "role": "admin",
                "id": admin.admin_id,
                "login": admin.email,
                "status": admin.status,
                "created_at": admin.created_at.isoformat() if admin.created_at else None,
            }
        )

    if role == "organizer":
        organizer = OrganizerAccount.objects.filter(organizer_account_id=account_id).first()
        if not organizer:
            return JsonResponse({"error": "Account not found"}, status=404)
        return JsonResponse(
            {
                "role": "organizer",
                "id": organizer.organizer_account_id,
                "login": organizer.email or organizer.phone,
                "email": organizer.email,
                "phone": organizer.phone,
                "status": organizer.status,
                "created_at": organizer.created_at.isoformat() if organizer.created_at else None,
            }
        )

    if role == "user":
        user = UserAccount.objects.filter(user_id=account_id).first()
        if not user:
            return JsonResponse({"error": "Account not found"}, status=404)
        return JsonResponse(
            {
                "role": "user",
                "id": user.user_id,
                "login": user.email or user.phone,
                "email": user.email,
                "phone": user.phone,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "status": user.status,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
        )

    return JsonResponse({"error": "Unsupported role"}, status=400)


@csrf_exempt
@require_POST
def admin_create_user(request):
    _, err = _require_admin_token(request)
    if err:
        return err

    payload = _parse_json_body(request)
    if not payload:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    full_name = (payload.get("full_name") or "").strip()
    login = (payload.get("login") or "").strip()
    password = payload.get("password") or ""
    user_type = (payload.get("user_type") or "").strip().lower()

    if not full_name or not login or not password or not user_type:
        return JsonResponse(
            {"error": "full_name, login, password, user_type are required"},
            status=400,
        )

    if user_type not in {"user", "organizer"}:
        return JsonResponse({"error": "user_type must be 'user' or 'organizer'"}, status=400)

    if "@" in login:
        email = login
        phone = None
    else:
        email = None
        phone = login

    if user_type == "user":
        # Split FIO into first and last name fields required by current schema.
        parts = full_name.split()
        first_name = parts[0]
        last_name = " ".join(parts[1:]) if len(parts) > 1 else "-"

        if email and UserAccount.objects.filter(email__iexact=email).exists():
            return JsonResponse({"error": "User with this email already exists"}, status=409)
        if phone and UserAccount.objects.filter(phone=phone).exists():
            return JsonResponse({"error": "User with this phone already exists"}, status=409)

        account = UserAccount.objects.create(
            email=email,
            phone=phone,
            password_hash=make_password(password),
            first_name=first_name,
            last_name=last_name,
            status=UserAccount.STATUS_ACTIVE,
        )
        return JsonResponse(
            {
                "id": account.user_id,
                "role": "user",
                "login": account.email or account.phone,
                "full_name": f"{account.first_name} {account.last_name}".strip(),
            },
            status=201,
        )

    if email and OrganizerAccount.objects.filter(email__iexact=email).exists():
        return JsonResponse({"error": "Organizer with this email already exists"}, status=409)
    if phone and OrganizerAccount.objects.filter(phone=phone).exists():
        return JsonResponse({"error": "Organizer with this phone already exists"}, status=409)
    if not email:
        return JsonResponse(
            {"error": "Organizer login must be an email in current schema"},
            status=400,
        )

    organizer = OrganizerAccount.objects.create(
        email=email,
        phone=phone,
        password_hash=make_password(password),
        status=OrganizerAccount.STATUS_ACTIVE,
    )
    return JsonResponse(
        {
            "id": organizer.organizer_account_id,
            "role": "organizer",
            "login": organizer.email or organizer.phone,
            "full_name": full_name,
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["GET", "PUT"])
def organizer_company(request):
    token_payload, err = _require_role_token(request, "organizer")
    if err:
        return err

    organizer_account = OrganizerAccount.objects.filter(
        organizer_account_id=token_payload.get("id")
    ).first()
    if not organizer_account:
        return JsonResponse({"error": "Organizer account not found"}, status=404)

    profile, _ = OrganizerProfile.objects.get_or_create(
        organizer_account=organizer_account,
        defaults={
            "display_name": organizer_account.email
            or organizer_account.phone
            or f"РћСЂРіР°РЅРёР·Р°С‚РѕСЂ {organizer_account.organizer_account_id}",
        },
    )

    if request.method == "GET":
        details = OrganizerDetails.objects.filter(organizer=profile).first()
        return JsonResponse(
            {
                "company": _organizer_profile_payload(profile),
                "details": _organizer_details_payload(details),
            }
        )

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    company = payload.get("company") or {}
    details_payload = payload.get("details") or {}

    profile_fields = [
        "display_name",
        "phone",
        "telegram",
        "whatsapp",
        "website_url",
        "address_text",
        "contact_person",
        "about_text",
    ]
    for field in profile_fields:
        if field in company:
            setattr(profile, field, company.get(field))
    profile.save()

    details = OrganizerDetails.objects.filter(organizer=profile).first()
    if not details and details_payload:
        details = OrganizerDetails.objects.create(
            organizer=profile,
            short_legal_name=details_payload.get("short_legal_name") or profile.display_name,
            full_legal_name=details_payload.get("full_legal_name") or profile.display_name,
            legal_address=details_payload.get("legal_address") or "РќРµ СѓРєР°Р·Р°РЅ",
            inn=details_payload.get("inn") or "0000000000",
            ogrn=details_payload.get("ogrn") or None,
            kpp=details_payload.get("kpp") or None,
            org_type=details_payload.get("org_type")
            or OrganizerDetails.ORG_TYPE_LEGAL_ENTITY,
            registration_date=details_payload.get("registration_date") or None,
            head_full_name=details_payload.get("head_full_name") or None,
            head_position=details_payload.get("head_position") or None,
            okved=details_payload.get("okved") or None,
            okopf=details_payload.get("okopf") or None,
            opf_name=details_payload.get("opf_name") or None,
        )
    elif details:
        details_fields = [
            "short_legal_name",
            "full_legal_name",
            "legal_address",
            "inn",
            "ogrn",
            "kpp",
            "org_type",
            "registration_date",
            "head_full_name",
            "head_position",
            "okved",
            "okopf",
            "opf_name",
        ]
        for field in details_fields:
            if field in details_payload:
                setattr(details, field, details_payload.get(field))
        details.save()

    return JsonResponse(
        {
            "company": _organizer_profile_payload(profile),
            "details": _organizer_details_payload(details),
        }
    )


@csrf_exempt
@require_http_methods(["GET", "POST"])
def organizer_events(request):
    profile, err = _organizer_profile_by_token(request)
    if err:
        return err

    if request.method == "GET":
        events = (
            Event.objects.filter(organizer=profile)
            .order_by("-event_id")
            .select_related("category", "venue")
            .prefetch_related("sessions")
        )
        payload = [_event_card_payload(request, event) for event in events]
        return JsonResponse({"events": payload})

    body = _parse_json_body(request)
    if body is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    event, create_err = _create_or_update_event_from_body(profile, body, event=None)
    if create_err:
        return create_err
    return JsonResponse(_event_detail_payload(request, event), status=201)


def _organizer_profile_by_token(request):
    token_payload, err = _require_role_token(request, "organizer")
    if err:
        return None, err
    organizer_account = OrganizerAccount.objects.filter(
        organizer_account_id=token_payload.get("id")
    ).first()
    if not organizer_account:
        return None, JsonResponse({"error": "Organizer account not found"}, status=404)
    profile, _ = OrganizerProfile.objects.get_or_create(
        organizer_account=organizer_account,
        defaults={
            "display_name": organizer_account.email
            or organizer_account.phone
            or f"Организатор {organizer_account.organizer_account_id}",
        },
    )
    return profile, None


def _event_image_url(request, file_field):
    if not file_field:
        return None
    url = getattr(file_field, "url", None) or str(file_field)
    if not url:
        return None
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return request.build_absolute_uri(url)


def _event_cover_url(request, event):
    if not event.cover_image_url:
        return None
    if event.cover_image_url.startswith("http://") or event.cover_image_url.startswith("https://"):
        return event.cover_image_url
    return request.build_absolute_uri(event.cover_image_url)


def _event_card_payload(request, event):
    sessions = list(event.sessions.order_by("starts_at"))
    first_session = sessions[0] if sessions else None
    return {
        "event_id": event.event_id,
        "title": event.title,
        "status": event.status,
        "description": event.description or "",
        "category": event.category.name if event.category else None,
        "venue_name": event.venue.name if event.venue else None,
        "venue_city": event.venue.city if event.venue else None,
        "venue_address": event.venue.address if event.venue else None,
        "cover_image_url": _event_cover_url(request, event),
        "starts_at": first_session.starts_at.isoformat() if first_session else None,
        "sessions_count": len(sessions),
    }


def _event_detail_payload(request, event):
    event = (
        Event.objects.select_related("category", "venue")
        .prefetch_related("sessions__ticket_types", "images")
        .get(pk=event.pk)
    )
    sessions_payload = []
    for session in event.sessions.all().order_by("starts_at"):
        sessions_payload.append(
            {
                "session_id": session.session_id,
                "starts_at": session.starts_at.isoformat(),
                "ends_at": session.ends_at.isoformat() if session.ends_at else None,
                "capacity": session.capacity,
                "ticket_types": [
                    {
                        "ticket_type_id": ticket.ticket_type_id,
                        "name": ticket.name,
                        "price": str(ticket.price),
                        "currency": ticket.currency,
                        "qty_total": ticket.qty_total,
                    }
                    for ticket in session.ticket_types.all().order_by("ticket_type_id")
                ],
            }
        )
    images_payload = [
        {
            "image_id": image.image_id,
            "url": _event_image_url(request, image.image),
            "sort_order": image.sort_order,
        }
        for image in event.images.filter(sort_order__gt=0).order_by("sort_order", "image_id")
    ]
    return {
        "event_id": event.event_id,
        "title": event.title,
        "status": event.status,
        "description": event.description or "",
        "age_min": event.age_min,
        "age_max": event.age_max,
        "category_name": event.category.name if event.category else "",
        "venue_name": event.venue.name if event.venue else "",
        "venue_city": event.venue.city if event.venue else "",
        "venue_address": event.venue.address if event.venue else "",
        "cover_image_url": _event_cover_url(request, event),
        "sessions": sessions_payload,
        "images": images_payload,
    }


def _normalize_status(raw_status):
    status = (raw_status or Event.STATUS_DRAFT).strip()
    if status not in {
        Event.STATUS_DRAFT,
        Event.STATUS_ON_MODERATION,
        Event.STATUS_PUBLISHED,
        Event.STATUS_REJECTED,
        Event.STATUS_ARCHIVED,
    }:
        return Event.STATUS_DRAFT
    return status


def _build_event_relations(body):
    category_name = (body.get("category_name") or "").strip() or "Без категории"
    venue_city = (body.get("venue_city") or "").strip() or "Не указан"
    venue_address = (body.get("venue_address") or "").strip() or "Не указан"
    venue_title = (body.get("venue_name") or "").strip() or f"{venue_city}, {venue_address}"
    category, _ = Category.objects.get_or_create(name=category_name)
    venue, _ = Venue.objects.get_or_create(
        name=venue_title,
        city=venue_city,
        address=venue_address,
    )
    return category, venue


def _parse_sessions_payload(raw_sessions, starts_at):
    normalized = []
    for session in raw_sessions or []:
        date_str = (session.get("date") or "").strip()
        start_time = (session.get("start_time") or "").strip()
        end_time = (session.get("end_time") or "").strip()
        capacity = session.get("capacity")
        if not date_str or not start_time:
            continue
        try:
            starts_dt = datetime.fromisoformat(f"{date_str}T{start_time}")
            ends_dt = datetime.fromisoformat(f"{date_str}T{end_time}") if end_time else None
        except ValueError:
            continue
        if timezone.is_naive(starts_dt):
            starts_dt = timezone.make_aware(starts_dt, timezone.get_current_timezone())
        if ends_dt and timezone.is_naive(ends_dt):
            ends_dt = timezone.make_aware(ends_dt, timezone.get_current_timezone())
        normalized.append(
            {
                "starts_at": starts_dt,
                "ends_at": ends_dt,
                "capacity": capacity if capacity not in ("", None) else None,
            }
        )
    if not normalized and starts_at:
        try:
            starts_dt = datetime.fromisoformat(starts_at.replace("Z", "+00:00"))
            if timezone.is_naive(starts_dt):
                starts_dt = timezone.make_aware(starts_dt, timezone.get_current_timezone())
            normalized.append({"starts_at": starts_dt, "ends_at": None, "capacity": None})
        except ValueError:
            pass
    return normalized


def _create_event_sessions_and_tickets(event, sessions_payload, ticket_types_payload):
    created_sessions = []
    for session in sessions_payload:
        created_sessions.append(
            EventSession.objects.create(
                event=event,
                starts_at=session["starts_at"],
                ends_at=session["ends_at"],
                capacity=session["capacity"],
            )
        )
    if created_sessions and ticket_types_payload:
        for session_obj in created_sessions:
            for ticket in ticket_types_payload:
                name = (ticket.get("name") or "").strip()
                price = ticket.get("price")
                if not name or price in ("", None):
                    continue
                qty_total = ticket.get("qty_total")
                currency = (ticket.get("currency") or "RUB").strip() or "RUB"
                TicketType.objects.create(
                    session=session_obj,
                    name=name,
                    price=price,
                    currency=currency,
                    qty_total=qty_total if qty_total not in ("", None) else None,
                )


def _create_or_update_event_from_body(profile, body, event=None):
    title = (body.get("title") or "").strip()
    if not title:
        return None, JsonResponse({"error": "title is required"}, status=400)

    category, venue = _build_event_relations(body)
    description = (body.get("description") or "").strip() or None
    status = _normalize_status(body.get("status"))
    age_min = body.get("age_min")
    age_max = body.get("age_max")
    if age_min in ("", None):
        age_min = None
    if age_max in ("", None):
        age_max = None

    is_update = event is not None
    if not event:
        event = Event(organizer=profile)
    event.category = category
    event.venue = venue
    event.title = title
    event.description = description
    event.status = status
    event.age_min = age_min
    event.age_max = age_max
    event.save()

    starts_at = (body.get("starts_at") or "").strip()
    sessions_payload = _parse_sessions_payload(body.get("sessions"), starts_at)
    ticket_types_payload = body.get("ticket_types") or []

    if is_update:
        event.sessions.all().delete()
    _create_event_sessions_and_tickets(event, sessions_payload, ticket_types_payload)
    return event, None


@csrf_exempt
@require_http_methods(["GET", "PUT"])
def organizer_event_detail(request, event_id):
    profile, err = _organizer_profile_by_token(request)
    if err:
        return err
    event = (
        Event.objects.filter(event_id=event_id, organizer=profile)
        .select_related("category", "venue")
        .first()
    )
    if not event:
        return JsonResponse({"error": "Event not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(_event_detail_payload(request, event))

    body = _parse_json_body(request)
    if body is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    updated_event, update_err = _create_or_update_event_from_body(profile, body, event=event)
    if update_err:
        return update_err
    return JsonResponse(_event_detail_payload(request, updated_event))


@csrf_exempt
@require_POST
def organizer_event_images(request, event_id):
    profile, err = _organizer_profile_by_token(request)
    if err:
        return err
    event = Event.objects.filter(event_id=event_id, organizer=profile).first()
    if not event:
        return JsonResponse({"error": "Event not found"}, status=404)

    cover_file = request.FILES.get("cover_image")
    gallery_files = request.FILES.getlist("gallery_images")
    deleted_gallery_ids_raw = (request.POST.get("deleted_gallery_ids") or "").strip()
    clear_cover = (request.POST.get("clear_cover") or "").strip() in {"1", "true", "True"}

    if len(gallery_files) > 5:
        return JsonResponse({"error": "gallery_images must be <= 5 files"}, status=400)

    deleted_gallery_ids = []
    if deleted_gallery_ids_raw:
        try:
            parsed = json.loads(deleted_gallery_ids_raw)
            if isinstance(parsed, list):
                deleted_gallery_ids = [int(x) for x in parsed]
        except (ValueError, TypeError, json.JSONDecodeError):
            return JsonResponse({"error": "deleted_gallery_ids must be a JSON list of ids"}, status=400)

    def _is_image(file_obj):
        return str(file_obj.content_type or "").startswith("image/")

    if cover_file and not _is_image(cover_file):
        return JsonResponse({"error": "cover_image must be an image"}, status=400)
    for gallery_file in gallery_files:
        if not _is_image(gallery_file):
            return JsonResponse({"error": "all gallery_images must be images"}, status=400)

    if deleted_gallery_ids:
        event.images.filter(sort_order__gt=0, image_id__in=deleted_gallery_ids).delete()

    if clear_cover and not cover_file:
        event.images.filter(sort_order=0).delete()
        event.cover_image_url = None
        event.save(update_fields=["cover_image_url"])

    current_gallery_count = event.images.filter(sort_order__gt=0).count()
    if current_gallery_count + len(gallery_files) > 5:
        return JsonResponse({"error": "total gallery images must be <= 5"}, status=400)

    if cover_file:
        event.images.filter(sort_order=0).delete()
        cover_record = EventImage.objects.create(event=event, image=cover_file, sort_order=0)
        event.cover_image_url = cover_record.image.url
        event.save(update_fields=["cover_image_url"])

    if gallery_files:
        last_sort = (
            event.images.filter(sort_order__gt=0)
            .order_by("-sort_order")
            .values_list("sort_order", flat=True)
            .first()
            or 0
        )
        for index, gallery_file in enumerate(gallery_files, start=1):
            EventImage.objects.create(event=event, image=gallery_file, sort_order=last_sort + index)

    return JsonResponse(_event_detail_payload(request, event))
