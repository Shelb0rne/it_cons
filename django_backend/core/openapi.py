import json

from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_GET


def _absolute_url(request, path):
    return request.build_absolute_uri(path)


def _schema(request):
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "IT Cons API",
            "version": "1.1.0",
            "description": "OpenAPI schema for the Django backend. Bearer token comes from POST /api/auth/login.",
        },
        "servers": [{"url": f"{request.scheme}://{request.get_host()}"}],
        "tags": [{"name": x} for x in ["System", "Public", "Auth", "User", "Organizer", "Admin"]],
        "components": {
            "securitySchemes": {
                "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "Token"}
            },
            "schemas": {
                "Health": {"type": "object", "properties": {"status": {"type": "string"}}},
                "Error": {"type": "object", "properties": {"error": {"type": "string"}}, "required": ["error"]},
                "SeatConflictError": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"},
                        "unavailable_seat_ids": {"type": "array", "items": {"type": "integer"}},
                    },
                    "required": ["error", "unavailable_seat_ids"],
                },
                "OkResponse": {"type": "object", "properties": {"ok": {"type": "boolean"}}},
                "AuthTokenResponse": {
                    "type": "object",
                    "properties": {
                        "token": {"type": "string"},
                        "user": {"type": "object"},
                    },
                },
                "AuthMeResponse": {"type": "object", "properties": {"role": {"type": "string"}, "id": {"type": "integer"}, "login": {"type": "string"}, "email": {"type": "string"}, "phone": {"type": "string"}, "first_name": {"type": "string"}, "last_name": {"type": "string"}, "status": {"type": "string"}, "created_at": {"type": "string"}}},
                "EventCard": {"type": "object", "properties": {"event_id": {"type": "integer"}, "title": {"type": "string"}, "description": {"type": "string"}, "status": {"type": "string"}, "age_min": {"type": "integer"}, "age_max": {"type": "integer"}, "category": {"type": "string"}, "venue_name": {"type": "string"}, "venue_city": {"type": "string"}, "venue_address": {"type": "string"}, "starts_at": {"type": "string"}, "cover_image_url": {"type": "string"}, "min_price": {"type": "string"}}},
                "EventListResponse": {
                    "type": "object",
                    "properties": {"events": {"type": "array", "items": {"$ref": "#/components/schemas/EventCard"}}},
                },
                "TicketType": {"type": "object", "properties": {"ticket_type_id": {"type": "integer"}, "name": {"type": "string"}, "price": {"type": "string"}, "currency": {"type": "string"}, "qty_total": {"type": "integer"}}},
                "EventSession": {"type": "object", "properties": {"session_id": {"type": "integer"}, "starts_at": {"type": "string"}, "ends_at": {"type": "string"}, "capacity": {"type": "integer"}, "ticket_types": {"type": "array", "items": {"$ref": "#/components/schemas/TicketType"}}}},
                "EventImage": {"type": "object", "properties": {"image_id": {"type": "integer"}, "url": {"type": "string"}, "sort_order": {"type": "integer"}}},
                "NearbyPlace": {"type": "object", "properties": {"place_id": {"type": "integer"}, "venue_id": {"type": "integer"}, "title": {"type": "string"}, "description": {"type": "string"}, "working_hours": {"type": "string"}, "average_check": {"type": "string"}, "travel_time_minutes": {"type": "integer"}, "image_url": {"type": "string"}, "venue_name": {"type": "string"}, "venue_city": {"type": "string"}, "venue_address": {"type": "string"}}},
                "EventDetailResponse": {"type": "object", "properties": {"event_id": {"type": "integer"}, "title": {"type": "string"}, "status": {"type": "string"}, "moderation_comment": {"type": "string"}, "description": {"type": "string"}, "age_min": {"type": "integer"}, "age_max": {"type": "integer"}, "category_name": {"type": "string"}, "venue_name": {"type": "string"}, "venue_city": {"type": "string"}, "venue_address": {"type": "string"}, "cover_image_url": {"type": "string"}, "sessions": {"type": "array", "items": {"$ref": "#/components/schemas/EventSession"}}, "images": {"type": "array", "items": {"$ref": "#/components/schemas/EventImage"}}, "nearby_places": {"type": "array", "items": {"$ref": "#/components/schemas/NearbyPlace"}}}},
                "SeatItem": {"type": "object", "properties": {"seat_id": {"type": "integer"}, "hall_name": {"type": "string"}, "row_number": {"type": "string"}, "seat_number": {"type": "string"}, "is_available": {"type": "boolean"}}},
                "SeatMapResponse": {"type": "object", "properties": {"event_id": {"type": "integer"}, "title": {"type": "string"}, "venue_name": {"type": "string"}, "venue_city": {"type": "string"}, "venue_address": {"type": "string"}, "cover_image_url": {"type": "string"}, "active_session_id": {"type": "integer"}, "sessions": {"type": "array", "items": {"$ref": "#/components/schemas/EventSession"}}, "seats": {"type": "array", "items": {"$ref": "#/components/schemas/SeatItem"}}}},
                "ObjectResponse": {"type": "object"},
                "ListResponse": {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object"}}}},
                "FavoritesResponse": {
                    "type": "object",
                    "properties": {
                        "event_ids": {"type": "array", "items": {"type": "integer"}},
                        "events": {"type": "array", "items": {"$ref": "#/components/schemas/EventCard"}},
                    },
                },
                "SelectedSeat": {"type": "object", "properties": {"seat_id": {"type": "integer"}, "row_number": {"type": "string"}, "seat_number": {"type": "string"}}},
                "ReservationResponse": {"type": "object", "properties": {"reservation_id": {"type": "integer"}, "expires_at": {"type": "string"}, "created_at": {"type": "string"}, "event_id": {"type": "integer"}, "title": {"type": "string"}, "cover_image_url": {"type": "string"}, "venue_name": {"type": "string"}, "venue_city": {"type": "string"}, "venue_address": {"type": "string"}, "session_id": {"type": "integer"}, "starts_at": {"type": "string"}, "ticket_type_id": {"type": "integer"}, "ticket_type_name": {"type": "string"}, "unit_price": {"type": "string"}, "currency": {"type": "string"}, "seat_ids": {"type": "array", "items": {"type": "integer"}}, "selected_seats": {"type": "array", "items": {"$ref": "#/components/schemas/SelectedSeat"}}, "qty": {"type": "integer"}, "total_amount": {"type": "string"}}},
                "OrderPaymentResponse": {"type": "object", "properties": {"order_id": {"type": "integer"}, "status": {"type": "string"}, "paid_at": {"type": "string"}, "total_amount": {"type": "string"}, "currency": {"type": "string"}}},
                "BookingsResponse": {
                    "type": "object",
                    "properties": {
                        "current": {"type": "array", "items": {"type": "object"}},
                        "history": {"type": "array", "items": {"type": "object"}},
                    },
                },
                "UserProfileResponse": {"type": "object", "properties": {"role": {"type": "string"}, "id": {"type": "integer"}, "login": {"type": "string"}, "email": {"type": "string"}, "phone": {"type": "string"}, "first_name": {"type": "string"}, "last_name": {"type": "string"}, "status": {"type": "string"}, "created_at": {"type": "string"}}},
                "PaymentMethodResponse": {"type": "object", "properties": {"payment_method_id": {"type": "integer"}, "card_number": {"type": "string"}, "card_last4": {"type": "string"}, "card_brand": {"type": "string"}, "holder_name": {"type": "string"}, "expires_at": {"type": "string"}, "cvv_code": {"type": "string"}, "status": {"type": "string"}, "created_at": {"type": "string"}}},
                "PaymentMethodListResponse": {
                    "type": "object",
                    "properties": {"items": {"type": "array", "items": {"$ref": "#/components/schemas/PaymentMethodResponse"}}},
                },
                "NearbyPlacesResponse": {
                    "type": "object",
                    "properties": {
                        "items": {"type": "array", "items": {"$ref": "#/components/schemas/NearbyPlace"}},
                        "venues": {"type": "array", "items": {"type": "object"}},
                    },
                },
                "RefundResponse": {"type": "object", "properties": {"refund_id": {"type": "integer"}, "status": {"type": "string"}, "admin_comment": {"type": "string"}}},
                "RefundListItem": {"type": "object", "properties": {"refund_id": {"type": "integer"}, "order_id": {"type": "integer"}, "status": {"type": "string"}, "amount": {"type": "string"}, "currency": {"type": "string"}, "admin_comment": {"type": "string"}, "created_at": {"type": "string"}, "reviewed_at": {"type": "string"}, "user_id": {"type": "integer"}, "user_name": {"type": "string"}, "user_login": {"type": "string"}, "event_id": {"type": "integer"}, "event_title": {"type": "string"}, "starts_at": {"type": "string"}, "ticket_qty": {"type": "integer"}}},
                "RefundListResponse": {"type": "object", "properties": {"items": {"type": "array", "items": {"$ref": "#/components/schemas/RefundListItem"}}}},
                "LoginRequest": {
                    "type": "object",
                    "required": ["login", "password"],
                    "properties": {"login": {"type": "string"}, "password": {"type": "string"}},
                },
                "RegisterRequest": {
                    "type": "object",
                    "required": ["full_name", "login", "password"],
                    "properties": {
                        "full_name": {"type": "string"},
                        "login": {"type": "string"},
                        "password": {"type": "string"},
                        "user_type": {
                            "type": "string",
                            "enum": ["user", "organizer"],
                            "default": "user",
                        },
                    },
                },
                "ReservationCreateRequest": {
                    "type": "object",
                    "required": ["event_id", "session_id", "ticket_type_id", "seat_ids"],
                    "properties": {
                        "event_id": {"type": "integer"},
                        "session_id": {"type": "integer"},
                        "ticket_type_id": {"type": "integer"},
                        "seat_ids": {"type": "array", "items": {"type": "integer"}},
                    },
                },
                "ReservationPayRequest": {"type": "object", "properties": {"payment_method_id": {"type": "integer"}}},
                "PaymentMethodRequest": {
                    "type": "object",
                    "properties": {
                        "card_brand": {"type": "string"},
                        "card_number": {"type": "string"},
                        "holder_name": {"type": "string"},
                        "expires_at": {"type": "string"},
                        "cvv_code": {"type": "string"},
                        "status": {"type": "string"},
                    },
                },
                "PrivacySettings": {
                    "type": "object",
                    "properties": {
                        "show_profile_in_reviews": {"type": "boolean"},
                        "allow_email_notifications": {"type": "boolean"},
                        "allow_sms_notifications": {"type": "boolean"},
                    },
                },
                "AdminCreateUserRequest": {
                    "type": "object",
                    "required": ["full_name", "login", "password", "user_type"],
                    "properties": {
                        "full_name": {"type": "string"},
                        "login": {"type": "string"},
                        "password": {"type": "string"},
                        "user_type": {"type": "string"},
                    },
                },
                "RefundReviewRequest": {
                    "type": "object",
                    "required": ["action"],
                    "properties": {"action": {"type": "string"}, "admin_comment": {"type": "string"}},
                },
                "ModerationReviewRequest": {
                    "type": "object",
                    "required": ["action"],
                    "properties": {"action": {"type": "string"}, "moderation_comment": {"type": "string"}},
                },
                "OrganizerCompanyRequest": {"type": "object", "properties": {"company": {"type": "object"}, "details": {"type": "object"}}},
                "OrganizerEventRequest": {"type": "object", "properties": {"title": {"type": "string"}}},
                "OrganizerCompanyResponse": {"type": "object", "properties": {"company": {"type": "object", "properties": {"display_name": {"type": "string"}, "phone": {"type": "string"}, "telegram": {"type": "string"}, "whatsapp": {"type": "string"}, "website_url": {"type": "string"}, "address_text": {"type": "string"}, "contact_person": {"type": "string"}, "about_text": {"type": "string"}}}, "details": {"type": "object", "properties": {"short_legal_name": {"type": "string"}, "full_legal_name": {"type": "string"}, "legal_address": {"type": "string"}, "inn": {"type": "string"}, "ogrn": {"type": "string"}, "kpp": {"type": "string"}, "org_type": {"type": "string"}, "registration_date": {"type": "string"}, "head_full_name": {"type": "string"}, "head_position": {"type": "string"}, "okved": {"type": "string"}, "okopf": {"type": "string"}, "opf_name": {"type": "string"}}}}},
            },
        },
        "paths": {},
    }


def _json_body(schema_ref, required=True):
    return {"required": required, "content": {"application/json": {"schema": {"$ref": schema_ref}}}}


def _multipart_body(properties, required=None):
    schema = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return {"required": True, "content": {"multipart/form-data": {"schema": schema}}}


def _resp(description, schema_ref=None):
    data = {"description": description}
    if schema_ref:
        data["content"] = {"application/json": {"schema": {"$ref": schema_ref}}}
    return data


def _responses(ok=None, errors=None):
    result = {}
    if ok:
        for code, description, schema_ref in ok:
            result[str(code)] = _resp(description, schema_ref)
    if errors:
        for code, schema_ref in errors:
            label = {
                400: "Bad request",
                401: "Unauthorized",
                403: "Forbidden",
                404: "Not found",
                409: "Conflict",
                410: "Gone",
                500: "Internal server error",
            }[code]
            result[str(code)] = _resp(label, schema_ref)
    return result


def _errs(*codes, seat_conflict=False):
    result = []
    for code in codes:
        schema_ref = "#/components/schemas/SeatConflictError" if code == 409 and seat_conflict else "#/components/schemas/Error"
        result.append((code, schema_ref))
    return result


def _op(tag, summary, responses, security=None, parameters=None, request_body=None):
    item = {"tags": [tag], "summary": summary, "responses": responses}
    if security:
        item["security"] = security
    if parameters:
        item["parameters"] = parameters
    if request_body:
        item["requestBody"] = request_body
    return item


def _path_int(name):
    return {"name": name, "in": "path", "required": True, "schema": {"type": "integer"}}


def _query(name, schema_type="string"):
    return {"name": name, "in": "query", "required": False, "schema": {"type": schema_type}}


def _fill_paths(schema):
    bearer = [{"bearerAuth": []}]
    schema["paths"] = {
        "/health": {"get": _op("System", "Health check", _responses([(200, "OK", "#/components/schemas/Health")], _errs(500)))},
        "/api/events": {"get": _op("Public", "List published events", _responses([(200, "Events", "#/components/schemas/EventListResponse")], _errs(500)))},
        "/api/events/{event_id}": {"get": _op("Public", "Get event details", _responses([(200, "Event details", "#/components/schemas/EventDetailResponse")], _errs(404, 500)), parameters=[_path_int("event_id")])},
        "/api/events/{event_id}/seat-map": {"get": _op("Public", "Get seat map", _responses([(200, "Seat map", "#/components/schemas/SeatMapResponse")], _errs(400, 404, 500)), parameters=[_path_int("event_id"), _query("session_id", "integer")])},
        "/api/auth/login": {"post": _op("Auth", "Login", _responses([(200, "Token", "#/components/schemas/AuthTokenResponse")], _errs(400, 401, 403, 500)), request_body=_json_body("#/components/schemas/LoginRequest"))},
        "/api/auth/register": {"post": _op("Auth", "Register user or organizer", _responses([(201, "Registered", "#/components/schemas/AuthTokenResponse")], _errs(400, 409, 500)), request_body=_json_body("#/components/schemas/RegisterRequest"))},
        "/api/auth/me": {"get": _op("Auth", "Get current account", _responses([(200, "Account", "#/components/schemas/AuthMeResponse")], _errs(400, 401, 404, 500)), security=bearer)},
        "/api/user/profile": {
            "get": _op("User", "Get profile", _responses([(200, "Profile", "#/components/schemas/UserProfileResponse")], _errs(401, 403, 404, 500)), security=bearer),
            "put": _op("User", "Update profile", _responses([(200, "Updated", "#/components/schemas/UserProfileResponse")], _errs(400, 401, 403, 404, 409, 500)), security=bearer, request_body=_json_body("#/components/schemas/UserProfileResponse")),
        },
        "/api/user/bookings": {"get": _op("User", "Get bookings", _responses([(200, "Bookings", "#/components/schemas/BookingsResponse")], _errs(401, 403, 404, 500)), security=bearer)},
        "/api/user/reservations": {"post": _op("User", "Create reservation", _responses([(201, "Created", "#/components/schemas/ReservationResponse")], _errs(400, 401, 403, 404, 409, 500, seat_conflict=True)), security=bearer, request_body=_json_body("#/components/schemas/ReservationCreateRequest"))},
        "/api/user/reservations/{reservation_id}": {"get": _op("User", "Get reservation", _responses([(200, "Reservation", "#/components/schemas/ReservationResponse")], _errs(401, 403, 404, 410, 500)), security=bearer, parameters=[_path_int("reservation_id")])},
        "/api/user/reservations/{reservation_id}/pay": {"post": _op("User", "Pay reservation", _responses([(200, "Paid", "#/components/schemas/OrderPaymentResponse")], _errs(400, 401, 403, 404, 409, 410, 500, seat_conflict=True)), security=bearer, parameters=[_path_int("reservation_id")], request_body=_json_body("#/components/schemas/ReservationPayRequest", required=False))},
        "/api/user/favorites": {
            "get": _op("User", "List favorites", _responses([(200, "Favorites", "#/components/schemas/FavoritesResponse")], _errs(401, 403, 404, 500)), security=bearer),
            "post": _op("User", "Add to favorites", _responses([(201, "Added", "#/components/schemas/OkResponse")], _errs(400, 401, 403, 404, 500)), security=bearer, request_body={"required": True, "content": {"application/json": {"schema": {"type": "object", "required": ["event_id"], "properties": {"event_id": {"type": "integer"}}}}}}),
        },
        "/api/user/favorites/{event_id}": {"delete": _op("User", "Remove from favorites", _responses([(200, "Removed", "#/components/schemas/OkResponse")], _errs(401, 403, 404, 500)), security=bearer, parameters=[_path_int("event_id")])},
        "/api/user/payment-methods": {
            "get": _op("User", "List payment methods", _responses([(200, "Payment methods", "#/components/schemas/PaymentMethodListResponse")], _errs(401, 403, 404, 500)), security=bearer),
            "post": _op("User", "Create payment method", _responses([(201, "Created", "#/components/schemas/PaymentMethodResponse")], _errs(400, 401, 403, 404, 500)), security=bearer, request_body=_json_body("#/components/schemas/PaymentMethodRequest")),
        },
        "/api/user/payment-methods/{payment_method_id}": {
            "put": _op("User", "Update payment method", _responses([(200, "Updated", "#/components/schemas/PaymentMethodResponse")], _errs(400, 401, 403, 404, 500)), security=bearer, parameters=[_path_int("payment_method_id")], request_body=_json_body("#/components/schemas/PaymentMethodRequest")),
            "delete": _op("User", "Delete payment method", _responses([(200, "Deleted", "#/components/schemas/OkResponse")], _errs(401, 403, 404, 500)), security=bearer, parameters=[_path_int("payment_method_id")]),
        },
        "/api/user/privacy": {
            "get": _op("User", "Get privacy", _responses([(200, "Privacy", "#/components/schemas/PrivacySettings")], _errs(401, 403, 404, 500)), security=bearer),
            "put": _op("User", "Update privacy", _responses([(200, "Updated", "#/components/schemas/PrivacySettings")], _errs(400, 401, 403, 404, 500)), security=bearer, request_body=_json_body("#/components/schemas/PrivacySettings")),
        },
        "/api/user/orders/{order_id}/refund-request": {"post": _op("User", "Create refund request", _responses([(201, "Created", "#/components/schemas/RefundResponse")], _errs(400, 401, 403, 404, 409, 500)), security=bearer, parameters=[_path_int("order_id")])},
        "/api/organizer/company": {
            "get": _op("Organizer", "Get company", _responses([(200, "Company", "#/components/schemas/OrganizerCompanyResponse")], _errs(401, 403, 404, 500)), security=bearer),
            "put": _op("Organizer", "Update company", _responses([(200, "Updated", "#/components/schemas/OrganizerCompanyResponse")], _errs(400, 401, 403, 404, 500)), security=bearer, request_body=_json_body("#/components/schemas/OrganizerCompanyRequest")),
        },
        "/api/organizer/events": {
            "get": _op("Organizer", "List organizer events", _responses([(200, "Events", "#/components/schemas/EventListResponse")], _errs(401, 403, 404, 500)), security=bearer),
            "post": _op("Organizer", "Create event", _responses([(201, "Created", "#/components/schemas/EventDetailResponse")], _errs(400, 401, 403, 404, 500)), security=bearer, request_body=_json_body("#/components/schemas/OrganizerEventRequest")),
        },
        "/api/organizer/events/{event_id}": {
            "get": _op("Organizer", "Get organizer event", _responses([(200, "Event", "#/components/schemas/EventDetailResponse")], _errs(401, 403, 404, 500)), security=bearer, parameters=[_path_int("event_id")]),
            "put": _op("Organizer", "Update organizer event", _responses([(200, "Updated", "#/components/schemas/EventDetailResponse")], _errs(400, 401, 403, 404, 500)), security=bearer, parameters=[_path_int("event_id")], request_body=_json_body("#/components/schemas/OrganizerEventRequest")),
        },
        "/api/organizer/events/{event_id}/images": {"post": _op("Organizer", "Upload event images", _responses([(200, "Updated", "#/components/schemas/EventDetailResponse")], _errs(400, 401, 403, 404, 500)), security=bearer, parameters=[_path_int("event_id")], request_body=_multipart_body({"cover_image": {"type": "string", "format": "binary"}, "gallery_images": {"type": "array", "items": {"type": "string", "format": "binary"}}, "deleted_gallery_ids": {"type": "string"}, "clear_cover": {"type": "string"}}))},
        "/api/admin/me": {"get": _op("Admin", "Get admin account", _responses([(200, "Admin", "#/components/schemas/ObjectResponse")], _errs(401, 403, 404, 500)), security=bearer)},
        "/api/admin/users": {"post": _op("Admin", "Create user or organizer", _responses([(201, "Created", "#/components/schemas/ObjectResponse")], _errs(400, 401, 403, 404, 409, 500)), security=bearer, request_body=_json_body("#/components/schemas/AdminCreateUserRequest"))},
        "/api/admin/refunds": {"get": _op("Admin", "List refunds", _responses([(200, "Refunds", "#/components/schemas/RefundListResponse")], _errs(401, 403, 404, 500)), security=bearer, parameters=[_query("status")])},
        "/api/admin/refunds/{refund_id}/review": {"post": _op("Admin", "Review refund", _responses([(200, "Reviewed", "#/components/schemas/RefundResponse")], _errs(400, 401, 403, 404, 409, 500)), security=bearer, parameters=[_path_int("refund_id")], request_body=_json_body("#/components/schemas/RefundReviewRequest"))},
        "/api/admin/events/moderation": {"get": _op("Admin", "List moderation events", _responses([(200, "Events", "#/components/schemas/ListResponse")], _errs(401, 403, 404, 500)), security=bearer)},
        "/api/admin/events/{event_id}/review": {"post": _op("Admin", "Review event moderation", _responses([(200, "Reviewed", "#/components/schemas/ObjectResponse")], _errs(400, 401, 403, 404, 500)), security=bearer, parameters=[_path_int("event_id")], request_body=_json_body("#/components/schemas/ModerationReviewRequest"))},
        "/api/admin/nearby-places": {"get": _op("Admin", "List nearby places", _responses([(200, "Nearby places", "#/components/schemas/NearbyPlacesResponse")], _errs(401, 403, 404, 500)), security=bearer)},
        "/api/admin/nearby-places/create": {"post": _op("Admin", "Create nearby place", _responses([(201, "Created", "#/components/schemas/NearbyPlace")], _errs(400, 401, 403, 404, 500)), security=bearer, request_body=_multipart_body({"venue_id": {"type": "integer"}, "title": {"type": "string"}, "description": {"type": "string"}, "working_hours": {"type": "string"}, "average_check": {"type": "number"}, "travel_time_minutes": {"type": "integer"}, "image": {"type": "string", "format": "binary"}}, required=["venue_id", "title"]))},
        "/api/admin/nearby-places/{place_id}": {
            "post": _op("Admin", "Update nearby place", _responses([(200, "Updated", "#/components/schemas/NearbyPlace")], _errs(400, 401, 403, 404, 500)), security=bearer, parameters=[_path_int("place_id")], request_body=_multipart_body({"venue_id": {"type": "integer"}, "title": {"type": "string"}, "description": {"type": "string"}, "working_hours": {"type": "string"}, "average_check": {"type": "number"}, "travel_time_minutes": {"type": "integer"}, "clear_image": {"type": "boolean"}, "image": {"type": "string", "format": "binary"}})),
            "delete": _op("Admin", "Delete nearby place", _responses([(200, "Deleted", "#/components/schemas/OkResponse")], _errs(401, 403, 404, 500)), security=bearer, parameters=[_path_int("place_id")]),
        },
    }
    return schema


@require_GET
def openapi_schema(request):
    return JsonResponse(_fill_paths(_schema(request)))


@require_GET
def swagger_ui(request):
    schema_url = _absolute_url(request, reverse("openapi-schema"))
    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>IT Cons API Docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <style>body {{ margin: 0; background: #f5f5f7; }} .topbar {{ display: none; }}</style>
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.ui = SwaggerUIBundle({{
        url: {json.dumps(schema_url)},
        dom_id: "#swagger-ui",
        deepLinking: true,
        displayRequestDuration: true,
        persistAuthorization: true
      }});
    </script>
  </body>
</html>"""
    return HttpResponse(html)
