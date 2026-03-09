import json
from decimal import Decimal
from datetime import datetime, timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.core import signing
from django.db import transaction
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
    Favorite,
    Order,
    OrderTicket,
    OrganizerAccount,
    OrganizerDetails,
    OrganizerProfile,
    Payment,
    Refund,
    Reservation,
    ReservationItem,
    Seat,
    TicketType,
    UserAccount,
    UserPaymentMethod,
    UserPrivacySettings,
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
        Event.objects.filter(status=Event.STATUS_PUBLISHED)
        .select_related("category", "venue")
        .prefetch_related("sessions__ticket_types")
        .order_by("event_id")
    )
    payload = []
    for event in events:
        card = _public_event_card_payload(request, event, now)
        if card:
            payload.append(card)
    return JsonResponse({"events": payload})


@require_GET
def public_event_detail(request, event_id):
    event = (
        Event.objects.filter(event_id=event_id)
        .select_related("category", "venue")
        .first()
    )
    if not event:
        return JsonResponse({"error": "Event not found"}, status=404)
    return JsonResponse(_event_detail_payload(request, event))


def _public_event_card_payload(request, event, now):
    all_sessions = list(event.sessions.all())
    future_sessions = [s for s in all_sessions if s.starts_at >= now]

    # Show only events that still have at least one future session.
    if not future_sessions:
        return None

    first_session = None
    if future_sessions:
        future_sessions.sort(key=lambda x: x.starts_at)
        first_session = future_sessions[0]

    prices = []
    for session in future_sessions:
        for ticket in session.ticket_types.all():
            prices.append(ticket.price)
    min_price = min(prices) if prices else None

    return {
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


def _venue_layout_by_name(venue_name):
    normalized = (venue_name or "").strip().lower()
    if "театр музыки" in normalized:
        return {"rows": 8, "seats_per_row": 12, "hall_name": "Большой зал"}
    if "кц зил" in normalized:
        return {"rows": 10, "seats_per_row": 16, "hall_name": "Главный зал"}
    if "дом музыки" in normalized:
        return {"rows": 12, "seats_per_row": 14, "hall_name": "Светлановский зал"}
    if "александрин" in normalized:
        return {"rows": 11, "seats_per_row": 15, "hall_name": "Основная сцена"}
    if "бкз" in normalized:
        return {"rows": 14, "seats_per_row": 18, "hall_name": "Концертный зал"}
    return {"rows": 9, "seats_per_row": 12, "hall_name": "Основной зал"}


def _ensure_venue_seats(venue):
    existing = Seat.objects.filter(venue=venue)
    if existing.exists():
        return list(existing.order_by("row_number", "seat_number"))

    layout = _venue_layout_by_name(venue.name)
    created = []
    for row in range(1, layout["rows"] + 1):
        row_label = str(row)
        for num in range(1, layout["seats_per_row"] + 1):
            created.append(
                Seat(
                    venue=venue,
                    hall_name=layout["hall_name"],
                    row_number=row_label,
                    seat_number=str(num),
                )
            )
    Seat.objects.bulk_create(created)
    return list(Seat.objects.filter(venue=venue).order_by("row_number", "seat_number"))


def _occupied_seat_ids_for_session(session):
    _expire_stale_holds()
    now = timezone.now()
    reserved_ids = set(
        ReservationItem.objects.filter(
            session=session,
            reservation__expires_at__gte=now,
        )
        .exclude(seat_id__isnull=True)
        .values_list("seat_id", flat=True)
    )
    ordered_ids = set(
        OrderTicket.objects.filter(
            session=session,
            order__status__in={Order.STATUS_AWAITING_PAYMENT, Order.STATUS_PAID},
        )
        .exclude(seat_id__isnull=True)
        .values_list("seat_id", flat=True)
    )
    return reserved_ids | ordered_ids


def _expire_stale_holds():
    now = timezone.now()
    Reservation.objects.filter(expires_at__lt=now).delete()
    (
        Order.objects.filter(
            status=Order.STATUS_AWAITING_PAYMENT,
            created_at__lt=now - timedelta(minutes=15),
        )
        .update(status=Order.STATUS_EXPIRED)
    )


def _reservation_payload(request, reservation):
    items = list(
        reservation.items.select_related(
            "session__event__venue",
            "ticket_type",
            "seat",
        ).order_by("reservation_item_id")
    )
    if not items:
        return None

    first = items[0]
    session = first.session
    event = session.event if session else None
    venue = event.venue if event else None
    ticket_type = first.ticket_type
    currency = ticket_type.currency if ticket_type else "RUB"

    total_amount = Decimal("0")
    seat_ids = []
    selected_seats = []
    for item in items:
        price = item.ticket_type.price if item.ticket_type else Decimal("0")
        total_amount += price
        if item.seat_id:
            seat_ids.append(item.seat_id)
            selected_seats.append(
                {
                    "seat_id": item.seat_id,
                    "row_number": item.seat.row_number if item.seat else None,
                    "seat_number": item.seat.seat_number if item.seat else None,
                }
            )

    return {
        "reservation_id": reservation.reservation_id,
        "expires_at": reservation.expires_at.isoformat() if reservation.expires_at else None,
        "created_at": reservation.created_at.isoformat() if reservation.created_at else None,
        "event_id": event.event_id if event else None,
        "title": event.title if event else "",
        "cover_image_url": _event_cover_url(request, event) if event else None,
        "venue_name": venue.name if venue else "",
        "venue_city": venue.city if venue else "",
        "venue_address": venue.address if venue else "",
        "session_id": session.session_id if session else None,
        "starts_at": session.starts_at.isoformat() if session and session.starts_at else None,
        "ticket_type_id": ticket_type.ticket_type_id if ticket_type else None,
        "ticket_type_name": ticket_type.name if ticket_type else "",
        "unit_price": str(ticket_type.price) if ticket_type else "0",
        "currency": currency,
        "seat_ids": seat_ids,
        "selected_seats": selected_seats,
        "qty": len(items),
        "total_amount": str(total_amount),
    }


@require_GET
def public_event_seat_map(request, event_id):
    event = (
        Event.objects.filter(event_id=event_id, status=Event.STATUS_PUBLISHED)
        .select_related("venue")
        .prefetch_related("sessions__ticket_types")
        .first()
    )
    if not event:
        return JsonResponse({"error": "Event not found"}, status=404)

    sessions = list(event.sessions.all().order_by("starts_at"))
    if not sessions:
        return JsonResponse({"error": "No sessions for this event"}, status=400)

    requested_session_id = request.GET.get("session_id")
    active_session = None
    if requested_session_id:
        try:
            req_id = int(requested_session_id)
            active_session = next((s for s in sessions if s.session_id == req_id), None)
        except ValueError:
            active_session = None
    if not active_session:
        active_session = sessions[0]

    seats = _ensure_venue_seats(event.venue)
    occupied_ids = _occupied_seat_ids_for_session(active_session)

    seats_payload = [
        {
            "seat_id": seat.seat_id,
            "hall_name": seat.hall_name,
            "row_number": seat.row_number,
            "seat_number": seat.seat_number,
            "is_available": seat.seat_id not in occupied_ids,
        }
        for seat in seats
    ]

    sessions_payload = []
    for session in sessions:
        sessions_payload.append(
            {
                "session_id": session.session_id,
                "starts_at": session.starts_at.isoformat(),
                "ends_at": session.ends_at.isoformat() if session.ends_at else None,
                "ticket_types": [
                    {
                        "ticket_type_id": tt.ticket_type_id,
                        "name": tt.name,
                        "price": str(tt.price),
                        "currency": tt.currency,
                        "qty_total": tt.qty_total,
                    }
                    for tt in session.ticket_types.all().order_by("ticket_type_id")
                ],
            }
        )

    return JsonResponse(
        {
            "event_id": event.event_id,
            "title": event.title,
            "venue_name": event.venue.name if event.venue else "",
            "venue_city": event.venue.city if event.venue else "",
            "venue_address": event.venue.address if event.venue else "",
            "cover_image_url": _event_cover_url(request, event),
            "active_session_id": active_session.session_id,
            "sessions": sessions_payload,
            "seats": seats_payload,
        }
    )


@csrf_exempt
@require_POST
def user_create_reservation(request):
    user, err = _user_account_by_token(request)
    if err:
        return err

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    event_id = payload.get("event_id")
    session_id = payload.get("session_id")
    ticket_type_id = payload.get("ticket_type_id")
    seat_ids_raw = payload.get("seat_ids") or []

    if not event_id or not session_id or not ticket_type_id or not isinstance(seat_ids_raw, list):
        return JsonResponse(
            {"error": "event_id, session_id, ticket_type_id and seat_ids are required"},
            status=400,
        )

    try:
        seat_ids = sorted({int(x) for x in seat_ids_raw})
    except (TypeError, ValueError):
        return JsonResponse({"error": "seat_ids must be a list of integer ids"}, status=400)
    if not seat_ids:
        return JsonResponse({"error": "Select at least one seat"}, status=400)

    event = Event.objects.filter(event_id=event_id, status=Event.STATUS_PUBLISHED).select_related("venue").first()
    if not event:
        return JsonResponse({"error": "Event not found"}, status=404)

    session = EventSession.objects.filter(session_id=session_id, event=event).first()
    if not session:
        return JsonResponse({"error": "Session not found"}, status=404)

    ticket_type = TicketType.objects.filter(ticket_type_id=ticket_type_id, session=session).first()
    if not ticket_type:
        return JsonResponse({"error": "Ticket type not found"}, status=404)

    seats = list(Seat.objects.filter(venue=event.venue, seat_id__in=seat_ids))
    if len(seats) != len(seat_ids):
        return JsonResponse({"error": "Some seats are invalid for this venue"}, status=400)

    with transaction.atomic():
        locked_ids = _occupied_seat_ids_for_session(session)
        unavailable = [sid for sid in seat_ids if sid in locked_ids]
        if unavailable:
            return JsonResponse(
                {
                    "error": "Some seats are no longer available",
                    "unavailable_seat_ids": unavailable,
                },
                status=409,
            )

        reservation = Reservation.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        by_id = {seat.seat_id: seat for seat in seats}
        for sid in seat_ids:
            ReservationItem.objects.create(
                reservation=reservation,
                session=session,
                ticket_type=ticket_type,
                seat=by_id[sid],
            )

    total_amount = ticket_type.price * len(seat_ids)
    return JsonResponse(
        {
            "reservation_id": reservation.reservation_id,
            "expires_at": reservation.expires_at.isoformat(),
            "event_id": event.event_id,
            "session_id": session.session_id,
            "ticket_type_id": ticket_type.ticket_type_id,
            "seat_ids": seat_ids,
            "qty": len(seat_ids),
            "unit_price": str(ticket_type.price),
            "currency": ticket_type.currency,
            "total_amount": str(total_amount),
        },
        status=201,
    )


@require_GET
def user_reservation_detail(request, reservation_id):
    user, err = _user_account_by_token(request)
    if err:
        return err

    _expire_stale_holds()
    reservation = (
        Reservation.objects.filter(
            reservation_id=reservation_id,
            user=user,
        )
        .prefetch_related("items__session__event__venue", "items__ticket_type", "items__seat")
        .first()
    )
    if not reservation:
        return JsonResponse({"error": "Reservation not found"}, status=404)

    if reservation.expires_at and reservation.expires_at < timezone.now():
        reservation.delete()
        return JsonResponse({"error": "Reservation expired"}, status=410)

    data = _reservation_payload(request, reservation)
    if not data:
        reservation.delete()
        return JsonResponse({"error": "Reservation has no items"}, status=410)
    return JsonResponse(data)


@csrf_exempt
@require_POST
def user_pay_reservation(request, reservation_id):
    user, err = _user_account_by_token(request)
    if err:
        return err

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    payment_method_id = payload.get("payment_method_id")
    selected_payment_method = None
    if payment_method_id:
        selected_payment_method = UserPaymentMethod.objects.filter(
            payment_method_id=payment_method_id,
            user=user,
            status=UserPaymentMethod.STATUS_ACTIVE,
        ).first()
        if not selected_payment_method:
            return JsonResponse({"error": "Payment method not found"}, status=404)

    _expire_stale_holds()
    with transaction.atomic():
        reservation = (
            Reservation.objects.select_for_update()
            .filter(
                reservation_id=reservation_id,
                user=user,
            )
            .prefetch_related("items__session__event__venue", "items__ticket_type", "items__seat")
            .first()
        )
        if not reservation:
            return JsonResponse({"error": "Reservation not found"}, status=404)

        now = timezone.now()
        if reservation.expires_at and reservation.expires_at < now:
            reservation.delete()
            return JsonResponse({"error": "Reservation expired"}, status=410)

        items = list(reservation.items.all())
        if not items:
            reservation.delete()
            return JsonResponse({"error": "Reservation has no items"}, status=410)

        for item in items:
            if not item.seat_id:
                return JsonResponse({"error": "Seat is required for reservation item"}, status=400)
            occupied = _occupied_seat_ids_for_session(item.session)
            if item.seat_id in occupied:
                own_hold = ReservationItem.objects.filter(
                    session=item.session,
                    seat_id=item.seat_id,
                    reservation=reservation,
                ).exists()
                if not own_hold:
                    return JsonResponse(
                        {
                            "error": "Some seats are no longer available",
                            "unavailable_seat_ids": [item.seat_id],
                        },
                        status=409,
                    )

        total_amount = Decimal("0")
        currency = "RUB"
        for item in items:
            total_amount += item.ticket_type.price
            currency = item.ticket_type.currency

        order = Order.objects.create(
            user=user,
            status=Order.STATUS_PAID,
            total_amount=total_amount,
            currency=currency,
            paid_at=now,
        )

        for item in items:
            OrderTicket.objects.create(
                order=order,
                session=item.session,
                ticket_type=item.ticket_type,
                seat=item.seat,
                unit_price=item.ticket_type.price,
                currency=item.ticket_type.currency,
            )

        Payment.objects.create(
            order=order,
            provider_payment_id=(
                selected_payment_method.provider_method_id if selected_payment_method else None
            ),
            amount=total_amount,
            currency=currency,
            confirmed_at=now,
        )

        reservation.delete()

    return JsonResponse(
        {
            "order_id": order.order_id,
            "status": order.status,
            "paid_at": order.paid_at.isoformat() if order.paid_at else None,
            "total_amount": str(order.total_amount),
            "currency": order.currency,
        }
    )


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


def _user_profile_payload(user):
    return {
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


def _user_payment_payload(method):
    return {
        "payment_method_id": method.payment_method_id,
        "card_number": method.card_number,
        "card_last4": method.card_last4,
        "card_brand": method.card_brand,
        "holder_name": method.holder_name,
        "expires_at": method.expires_at,
        "cvv_code": method.cvv_code,
        "status": method.status,
        "created_at": method.created_at.isoformat() if method.created_at else None,
    }


def _user_privacy_payload(settings):
    return {
        "show_profile_in_reviews": settings.show_profile_in_reviews,
        "allow_email_notifications": settings.allow_email_notifications,
        "allow_sms_notifications": settings.allow_sms_notifications,
    }


def _user_account_by_token(request):
    token_payload, err = _require_role_token(request, "user")
    if err:
        return None, err
    user = UserAccount.objects.filter(user_id=token_payload.get("id")).first()
    if not user:
        return None, JsonResponse({"error": "User account not found"}, status=404)
    return user, None


@csrf_exempt
@require_http_methods(["GET", "PUT"])
def user_profile(request):
    user, err = _user_account_by_token(request)
    if err:
        return err

    if request.method == "GET":
        return JsonResponse(_user_profile_payload(user))

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    first_name = (payload.get("first_name") if "first_name" in payload else user.first_name) or ""
    last_name = (payload.get("last_name") if "last_name" in payload else user.last_name) or ""
    email_raw = payload.get("email") if "email" in payload else user.email
    phone_raw = payload.get("phone") if "phone" in payload else user.phone

    first_name = first_name.strip()
    last_name = last_name.strip()
    email = (email_raw or "").strip() or None
    phone = (phone_raw or "").strip() or None

    if not first_name or not last_name:
        return JsonResponse({"error": "first_name and last_name are required"}, status=400)
    if not email and not phone:
        return JsonResponse({"error": "email or phone is required"}, status=400)

    if email and UserAccount.objects.filter(email__iexact=email).exclude(user_id=user.user_id).exists():
        return JsonResponse({"error": "User with this email already exists"}, status=409)
    if phone and UserAccount.objects.filter(phone=phone).exclude(user_id=user.user_id).exists():
        return JsonResponse({"error": "User with this phone already exists"}, status=409)

    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.phone = phone
    user.save()

    return JsonResponse(_user_profile_payload(user))


@csrf_exempt
@require_http_methods(["GET", "POST"])
def user_favorites(request):
    user, err = _user_account_by_token(request)
    if err:
        return err

    if request.method == "GET":
        now = timezone.now()
        favorites = (
            Favorite.objects.filter(user=user)
            .select_related("event__category", "event__venue")
            .prefetch_related("event__sessions__ticket_types")
            .order_by("-id")
        )
        items = []
        for favorite in favorites:
            event = favorite.event
            if not event or event.status != Event.STATUS_PUBLISHED:
                continue
            card = _public_event_card_payload(request, event, now)
            if card:
                items.append(card)
        ids = [item["event_id"] for item in items]
        return JsonResponse({"event_ids": ids, "events": items})

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    event_id = payload.get("event_id")
    if not event_id:
        return JsonResponse({"error": "event_id is required"}, status=400)

    event = Event.objects.filter(event_id=event_id, status=Event.STATUS_PUBLISHED).first()
    if not event:
        return JsonResponse({"error": "Event not found"}, status=404)

    Favorite.objects.get_or_create(user=user, event=event)
    return JsonResponse({"ok": True}, status=201)


@csrf_exempt
@require_http_methods(["DELETE"])
def user_favorite_detail(request, event_id):
    user, err = _user_account_by_token(request)
    if err:
        return err

    Favorite.objects.filter(user=user, event_id=event_id).delete()
    return JsonResponse({"ok": True})


@require_GET
def user_bookings(request):
    user, err = _user_account_by_token(request)
    if err:
        return err

    _expire_stale_holds()
    now = timezone.now()

    current_payload = []

    orders = (
        Order.objects.filter(user=user)
        .prefetch_related("order_tickets__session__event__venue", "order_tickets__ticket_type", "order_tickets__seat")
        .order_by("-created_at")
    )

    for order in orders:
        tickets = list(order.order_tickets.all())
        if not tickets:
            continue
        starts = [t.session.starts_at for t in tickets if t.session and t.session.starts_at]
        if not starts:
            continue
        event_start = min(starts)
        if order.status == Order.STATUS_PAID and event_start >= now:
            first_ticket = tickets[0]
            event = first_ticket.session.event if first_ticket.session else None
            venue = event.venue if event else None
            latest_refund = order.refunds.order_by("-created_at").first()
            ticket_items = []
            for ticket in tickets:
                ticket_items.append(
                    {
                        "ticket_type": ticket.ticket_type.name if ticket.ticket_type else "",
                        "unit_price": str(ticket.unit_price),
                        "currency": ticket.currency,
                        "row_number": ticket.seat.row_number if ticket.seat else None,
                        "seat_number": ticket.seat.seat_number if ticket.seat else None,
                    }
                )
            current_payload.append(
                {
                    "kind": "paid_order",
                    "order_id": order.order_id,
                    "event_id": event.event_id if event else None,
                    "event_title": event.title if event else "",
                    "cover_image_url": _event_cover_url(request, event) if event else None,
                    "starts_at": event_start.isoformat(),
                    "venue_name": venue.name if venue else "",
                    "ticket_qty": len(tickets),
                    "total_amount": str(order.total_amount),
                    "currency": order.currency,
                    "status": "paid",
                    "days_left": max(0, (event_start.date() - now.date()).days),
                    "paid_at": order.paid_at.isoformat() if order.paid_at else None,
                    "tickets": ticket_items,
                    "refund": (
                        {
                            "refund_id": latest_refund.refund_id,
                            "status": latest_refund.status,
                            "admin_comment": latest_refund.admin_comment,
                            "created_at": latest_refund.created_at.isoformat()
                            if latest_refund.created_at
                            else None,
                            "reviewed_at": latest_refund.reviewed_at.isoformat()
                            if latest_refund.reviewed_at
                            else None,
                        }
                        if latest_refund
                        else None
                    ),
                }
            )

    history_payload = []
    for order in orders:
        latest_refund = order.refunds.order_by("-created_at").first()
        tickets_payload = []
        for ticket in order.order_tickets.all():
            session = ticket.session
            event = session.event if session else None
            venue = event.venue if event else None
            tickets_payload.append(
                {
                    "event_id": event.event_id if event else None,
                    "event_title": event.title if event else "",
                    "starts_at": session.starts_at.isoformat() if session and session.starts_at else None,
                    "venue_name": venue.name if venue else "",
                    "ticket_type": ticket.ticket_type.name if ticket.ticket_type else "",
                    "unit_price": str(ticket.unit_price),
                    "currency": ticket.currency,
                }
            )
        history_payload.append(
            {
                "order_id": order.order_id,
                "status": order.status,
                "total_amount": str(order.total_amount),
                "currency": order.currency,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "paid_at": order.paid_at.isoformat() if order.paid_at else None,
                "tickets": tickets_payload,
                "refund": (
                    {
                        "refund_id": latest_refund.refund_id,
                        "status": latest_refund.status,
                        "admin_comment": latest_refund.admin_comment,
                        "created_at": latest_refund.created_at.isoformat()
                        if latest_refund.created_at
                        else None,
                        "reviewed_at": latest_refund.reviewed_at.isoformat()
                        if latest_refund.reviewed_at
                        else None,
                    }
                    if latest_refund
                    else None
                ),
            }
        )

    current_payload.sort(key=lambda x: x.get("starts_at") or "")
    return JsonResponse({"current": current_payload, "history": history_payload})


@csrf_exempt
@require_POST
def user_request_refund(request, order_id):
    user, err = _user_account_by_token(request)
    if err:
        return err

    order = (
        Order.objects.filter(order_id=order_id, user=user)
        .prefetch_related("order_tickets__session")
        .first()
    )
    if not order:
        return JsonResponse({"error": "Order not found"}, status=404)
    if order.status != Order.STATUS_PAID:
        return JsonResponse({"error": "Refund is available only for paid orders"}, status=400)

    now = timezone.now()
    starts = [
        ticket.session.starts_at
        for ticket in order.order_tickets.all()
        if ticket.session and ticket.session.starts_at
    ]
    if starts and min(starts) <= now:
        return JsonResponse({"error": "Cannot request refund after event start"}, status=400)

    pending = order.refunds.filter(
        status__in=[Refund.STATUS_REQUESTED, Refund.STATUS_APPROVED, Refund.STATUS_PROCESSING]
    ).exists()
    if pending:
        return JsonResponse({"error": "Refund request is already in progress"}, status=409)

    refund = Refund.objects.create(
        order=order,
        status=Refund.STATUS_REQUESTED,
        amount=order.total_amount,
        currency=order.currency,
    )
    return JsonResponse(
        {
            "refund_id": refund.refund_id,
            "status": refund.status,
        },
        status=201,
    )


@require_GET
def admin_refunds(request):
    token_payload, err = _require_admin_token(request)
    if err:
        return err
    admin = AdminAccount.objects.filter(admin_id=token_payload.get("id")).first()
    if not admin:
        return JsonResponse({"error": "Admin account not found"}, status=404)

    status_filter = (request.GET.get("status") or "").strip().lower()
    qs = Refund.objects.select_related("order__user").order_by("-created_at")
    if status_filter in {
        Refund.STATUS_REQUESTED,
        Refund.STATUS_APPROVED,
        Refund.STATUS_PROCESSING,
        Refund.STATUS_SUCCEEDED,
        Refund.STATUS_REJECTED,
    }:
        qs = qs.filter(status=status_filter)

    items = []
    for refund in qs:
        order = refund.order
        user_obj = order.user if order else None
        user_login = ""
        user_name = ""
        if user_obj:
            user_login = user_obj.email or user_obj.phone or ""
            user_name = f"{user_obj.first_name or ''} {user_obj.last_name or ''}".strip()
        tickets = (
            order.order_tickets.select_related("session__event")
            .all()
            if order
            else []
        )
        first_ticket = tickets[0] if tickets else None
        event = first_ticket.session.event if first_ticket and first_ticket.session else None
        starts = [
            ticket.session.starts_at
            for ticket in tickets
            if ticket.session and ticket.session.starts_at
        ]
        items.append(
            {
                "refund_id": refund.refund_id,
                "order_id": order.order_id if order else None,
                "status": refund.status,
                "amount": str(refund.amount),
                "currency": refund.currency,
                "admin_comment": refund.admin_comment,
                "created_at": refund.created_at.isoformat() if refund.created_at else None,
                "reviewed_at": refund.reviewed_at.isoformat() if refund.reviewed_at else None,
                "user_id": user_obj.user_id if user_obj else None,
                "user_name": user_name,
                "user_login": user_login,
                "event_id": event.event_id if event else None,
                "event_title": event.title if event else "",
                "starts_at": min(starts).isoformat() if starts else None,
                "ticket_qty": len(tickets),
            }
        )
    return JsonResponse({"items": items})


@csrf_exempt
@require_POST
def admin_refund_review(request, refund_id):
    token_payload, err = _require_admin_token(request)
    if err:
        return err
    admin = AdminAccount.objects.filter(admin_id=token_payload.get("id")).first()
    if not admin:
        return JsonResponse({"error": "Admin account not found"}, status=404)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    action = (payload.get("action") or "").strip().lower()
    admin_comment = (payload.get("admin_comment") or "").strip()
    if action not in {"approve", "reject"}:
        return JsonResponse({"error": "action must be approve or reject"}, status=400)
    if action == "reject" and not admin_comment:
        return JsonResponse({"error": "admin_comment is required when rejecting"}, status=400)

    with transaction.atomic():
        refund = (
            Refund.objects.select_for_update()
            .select_related("order")
            .prefetch_related("order__order_tickets")
            .filter(refund_id=refund_id)
            .first()
        )
        if not refund:
            return JsonResponse({"error": "Refund request not found"}, status=404)
        if refund.status != Refund.STATUS_REQUESTED:
            return JsonResponse({"error": "Refund request already processed"}, status=409)

        order = refund.order
        if not order:
            return JsonResponse({"error": "Order not found"}, status=404)

        now = timezone.now()
        if action == "approve":
            refund.status = Refund.STATUS_SUCCEEDED
            refund.admin_comment = admin_comment or "Возврат одобрен"
            refund.reviewed_at = now
            refund.save(update_fields=["status", "admin_comment", "reviewed_at"])

            order.status = Order.STATUS_REFUNDED
            order.save(update_fields=["status"])
        else:
            refund.status = Refund.STATUS_REJECTED
            refund.admin_comment = admin_comment
            refund.reviewed_at = now
            refund.save(update_fields=["status", "admin_comment", "reviewed_at"])

    return JsonResponse(
        {
            "refund_id": refund.refund_id,
            "status": refund.status,
            "admin_comment": refund.admin_comment,
        }
    )


@csrf_exempt
@require_http_methods(["GET", "POST"])
def user_payment_methods(request):
    user, err = _user_account_by_token(request)
    if err:
        return err

    if request.method == "GET":
        items = UserPaymentMethod.objects.filter(user=user).order_by("-created_at")
        return JsonResponse({"items": [_user_payment_payload(item) for item in items]})

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    card_brand = (payload.get("card_brand") or "").strip()
    card_number = (payload.get("card_number") or "").strip()
    holder_name = (payload.get("holder_name") or "").strip()
    expires_at = (payload.get("expires_at") or "").strip()
    cvv_code = (payload.get("cvv_code") or "").strip()

    if not card_brand:
        return JsonResponse({"error": "card_brand is required"}, status=400)
    if len(card_number) != 12 or not card_number.isdigit():
        return JsonResponse({"error": "card_number must contain exactly 12 digits"}, status=400)
    if not holder_name:
        return JsonResponse({"error": "holder_name is required"}, status=400)
    if len(expires_at) != 5 or expires_at[2] != "/":
        return JsonResponse({"error": "expires_at must be in MM/YY format"}, status=400)
    mm, yy = expires_at.split("/")
    if not (mm.isdigit() and yy.isdigit() and 1 <= int(mm) <= 12):
        return JsonResponse({"error": "expires_at must be in MM/YY format"}, status=400)
    if len(cvv_code) not in {3, 4} or not cvv_code.isdigit():
        return JsonResponse({"error": "cvv_code must contain 3 or 4 digits"}, status=400)

    method = UserPaymentMethod.objects.create(
        user=user,
        card_number=card_number,
        card_last4=card_number[-4:],
        card_brand=card_brand,
        holder_name=holder_name,
        expires_at=expires_at,
        cvv_code=cvv_code,
        status=UserPaymentMethod.STATUS_ACTIVE,
    )
    return JsonResponse(_user_payment_payload(method), status=201)


@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def user_payment_method_detail(request, payment_method_id):
    user, err = _user_account_by_token(request)
    if err:
        return err

    method = UserPaymentMethod.objects.filter(
        payment_method_id=payment_method_id,
        user=user,
    ).first()
    if not method:
        return JsonResponse({"error": "Payment method not found"}, status=404)

    if request.method == "DELETE":
        method.delete()
        return JsonResponse({"ok": True})

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    if "card_brand" in payload:
        method.card_brand = (payload.get("card_brand") or "").strip() or None
    if "card_number" in payload:
        card_number = (payload.get("card_number") or "").strip()
        if len(card_number) != 12 or not card_number.isdigit():
            return JsonResponse({"error": "card_number must contain exactly 12 digits"}, status=400)
        method.card_number = card_number
        method.card_last4 = card_number[-4:]
    if "holder_name" in payload:
        method.holder_name = (payload.get("holder_name") or "").strip() or None
    if "expires_at" in payload:
        expires_at = (payload.get("expires_at") or "").strip()
        if len(expires_at) != 5 or expires_at[2] != "/":
            return JsonResponse({"error": "expires_at must be in MM/YY format"}, status=400)
        mm, yy = expires_at.split("/")
        if not (mm.isdigit() and yy.isdigit() and 1 <= int(mm) <= 12):
            return JsonResponse({"error": "expires_at must be in MM/YY format"}, status=400)
        method.expires_at = expires_at
    if "cvv_code" in payload:
        cvv_code = (payload.get("cvv_code") or "").strip()
        if len(cvv_code) not in {3, 4} or not cvv_code.isdigit():
            return JsonResponse({"error": "cvv_code must contain 3 or 4 digits"}, status=400)
        method.cvv_code = cvv_code
    if "status" in payload and payload.get("status") in {
        UserPaymentMethod.STATUS_ACTIVE,
        UserPaymentMethod.STATUS_DISABLED,
    }:
        method.status = payload.get("status")

    if not method.card_brand or not method.card_number or not method.holder_name or not method.expires_at or not method.cvv_code:
        return JsonResponse({"error": "card_brand, card_number, holder_name, expires_at, cvv_code are required"}, status=400)

    method.save()
    return JsonResponse(_user_payment_payload(method))


@csrf_exempt
@require_http_methods(["GET", "PUT"])
def user_privacy(request):
    user, err = _user_account_by_token(request)
    if err:
        return err

    settings, _ = UserPrivacySettings.objects.get_or_create(user=user)

    if request.method == "GET":
        return JsonResponse(_user_privacy_payload(settings))

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    if "show_profile_in_reviews" in payload:
        settings.show_profile_in_reviews = bool(payload.get("show_profile_in_reviews"))
    if "allow_email_notifications" in payload:
        settings.allow_email_notifications = bool(payload.get("allow_email_notifications"))
    if "allow_sms_notifications" in payload:
        settings.allow_sms_notifications = bool(payload.get("allow_sms_notifications"))

    settings.save()
    return JsonResponse(_user_privacy_payload(settings))


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
    if status == Event.STATUS_PUBLISHED and not sessions_payload:
        return None, JsonResponse(
            {"error": "At least one session is required to publish an event"},
            status=400,
        )

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





