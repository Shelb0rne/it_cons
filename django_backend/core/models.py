from django.db import models


class UserAccount(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_BLOCKED = "blocked"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "active"),
        (STATUS_BLOCKED, "blocked"),
    ]

    user_id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=32, unique=True, null=True, blank=True)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    class Meta:
        db_table = "user_account"


class OrganizerAccount(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_BLOCKED = "blocked"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "active"),
        (STATUS_BLOCKED, "blocked"),
    ]

    organizer_account_id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=32, unique=True, null=True, blank=True)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    class Meta:
        db_table = "organizer_account"


class AdminAccount(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_BLOCKED = "blocked"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "active"),
        (STATUS_BLOCKED, "blocked"),
    ]

    admin_id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    class Meta:
        db_table = "admin_account"


class OrganizerProfile(models.Model):
    organizer_id = models.BigAutoField(primary_key=True)
    organizer_account = models.OneToOneField(
        OrganizerAccount,
        on_delete=models.CASCADE,
        db_column="organizer_account_id",
        related_name="organizer_profile",
    )
    logo_url = models.URLField(null=True, blank=True)
    display_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, null=True, blank=True)
    telegram = models.CharField(max_length=255, null=True, blank=True)
    whatsapp = models.CharField(max_length=255, null=True, blank=True)
    website_url = models.URLField(null=True, blank=True)
    address_text = models.TextField(null=True, blank=True)
    contact_person = models.CharField(max_length=255, null=True, blank=True)
    about_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "organizer_profile"


class OrganizerDetails(models.Model):
    ORG_TYPE_LEGAL_ENTITY = "legal_entity"
    ORG_TYPE_IP = "ip"
    ORG_TYPE_SELF_EMPLOYED = "self_employed"
    ORG_TYPE_INDIVIDUAL = "individual"
    ORG_TYPE_CHOICES = [
        (ORG_TYPE_LEGAL_ENTITY, "legal_entity"),
        (ORG_TYPE_IP, "ip"),
        (ORG_TYPE_SELF_EMPLOYED, "self_employed"),
        (ORG_TYPE_INDIVIDUAL, "individual"),
    ]

    legal_details_id = models.BigAutoField(primary_key=True)
    organizer = models.OneToOneField(
        OrganizerProfile,
        on_delete=models.CASCADE,
        db_column="organizer_id",
        related_name="organizer_details",
    )
    short_legal_name = models.CharField(max_length=255)
    full_legal_name = models.CharField(max_length=512)
    legal_address = models.TextField()
    inn = models.CharField(max_length=12)
    ogrn = models.CharField(max_length=15, null=True, blank=True)
    kpp = models.CharField(max_length=9, null=True, blank=True)
    org_type = models.CharField(max_length=20, choices=ORG_TYPE_CHOICES)
    registration_date = models.DateField(null=True, blank=True)
    head_full_name = models.CharField(max_length=255, null=True, blank=True)
    head_position = models.CharField(max_length=255, null=True, blank=True)
    okved = models.CharField(max_length=32, null=True, blank=True)
    okopf = models.CharField(max_length=16, null=True, blank=True)
    opf_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "organizer_details"


class OrganizerVerification(models.Model):
    STATUS_NOT_SUBMITTED = "not_submitted"
    STATUS_SUBMITTED = "submitted"
    STATUS_IN_REVIEW = "in_review"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_NOT_SUBMITTED, "not_submitted"),
        (STATUS_SUBMITTED, "submitted"),
        (STATUS_IN_REVIEW, "in_review"),
        (STATUS_APPROVED, "approved"),
        (STATUS_REJECTED, "rejected"),
    ]

    verification_id = models.BigAutoField(primary_key=True)
    organizer = models.OneToOneField(
        OrganizerProfile,
        on_delete=models.CASCADE,
        db_column="organizer_id",
        related_name="verification",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_SUBMITTED,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reject_reason = models.TextField(null=True, blank=True)
    reviewed_by_admin = models.ForeignKey(
        AdminAccount,
        on_delete=models.SET_NULL,
        db_column="reviewed_by_admin_id",
        related_name="reviewed_verifications",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "organizer_verification"


class OrganizerDocument(models.Model):
    DOC_TYPE_INN_CERT = "inn_certificate"
    DOC_TYPE_HEAD_ORDER = "head_appointment_order"
    DOC_TYPE_OTHER = "other"
    DOC_TYPE_CHOICES = [
        (DOC_TYPE_INN_CERT, "inn_certificate"),
        (DOC_TYPE_HEAD_ORDER, "head_appointment_order"),
        (DOC_TYPE_OTHER, "other"),
    ]

    document_id = models.BigAutoField(primary_key=True)
    verification = models.ForeignKey(
        OrganizerVerification,
        on_delete=models.CASCADE,
        db_column="verification_id",
        related_name="documents",
    )
    doc_type = models.CharField(max_length=64, choices=DOC_TYPE_CHOICES)
    file_url = models.URLField()

    class Meta:
        db_table = "organizer_document"


class Category(models.Model):
    category_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "category"


class Venue(models.Model):
    venue_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=128)
    address = models.CharField(max_length=512)

    class Meta:
        db_table = "venue"


class Event(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_ON_MODERATION = "on_moderation"
    STATUS_PUBLISHED = "published"
    STATUS_REJECTED = "rejected"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "draft"),
        (STATUS_ON_MODERATION, "on_moderation"),
        (STATUS_PUBLISHED, "published"),
        (STATUS_REJECTED, "rejected"),
        (STATUS_ARCHIVED, "archived"),
    ]

    event_id = models.BigAutoField(primary_key=True)
    organizer = models.ForeignKey(
        OrganizerProfile,
        on_delete=models.CASCADE,
        db_column="organizer_id",
        related_name="events",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        db_column="category_id",
        related_name="events",
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        db_column="venue_id",
        related_name="events",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    age_min = models.PositiveSmallIntegerField(null=True, blank=True)
    age_max = models.PositiveSmallIntegerField(null=True, blank=True)
    cover_image_url = models.URLField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    moderation_comment = models.TextField(null=True, blank=True)
    moderated_by_admin = models.ForeignKey(
        AdminAccount,
        on_delete=models.SET_NULL,
        db_column="moderated_by_admin_id",
        related_name="moderated_events",
        null=True,
        blank=True,
    )
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "event"


class EventSession(models.Model):
    session_id = models.BigAutoField(primary_key=True)
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        db_column="event_id",
        related_name="sessions",
    )
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = "event_session"


class TicketType(models.Model):
    ticket_type_id = models.BigAutoField(primary_key=True)
    session = models.ForeignKey(
        EventSession,
        on_delete=models.CASCADE,
        db_column="session_id",
        related_name="ticket_types",
    )
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")
    qty_total = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = "ticket_type"


class Seat(models.Model):
    seat_id = models.BigAutoField(primary_key=True)
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        db_column="venue_id",
        related_name="seats",
    )
    hall_name = models.CharField(max_length=255, null=True, blank=True)
    row_number = models.CharField(max_length=20)
    seat_number = models.CharField(max_length=20)

    class Meta:
        db_table = "seat"
        constraints = [
            models.UniqueConstraint(
                fields=["venue", "hall_name", "row_number", "seat_number"],
                name="uq_seat_per_hall",
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="favorites",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        db_column="event_id",
        related_name="favorited_by",
    )

    class Meta:
        db_table = "favorite"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "event"],
                name="uq_favorite_user_event",
            )
        ]


class Cart(models.Model):
    cart_id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(
        UserAccount,
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="cart",
    )
    expires_at = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart"


class CartTicket(models.Model):
    cart_tickets_id = models.BigAutoField(primary_key=True)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        db_column="cart_id",
        related_name="cart_tickets",
    )
    session = models.ForeignKey(
        EventSession,
        on_delete=models.CASCADE,
        db_column="session_id",
        related_name="cart_tickets",
    )
    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.CASCADE,
        db_column="ticket_type_id",
        related_name="cart_tickets",
    )
    seat = models.ForeignKey(
        Seat,
        on_delete=models.SET_NULL,
        db_column="seat_id",
        related_name="cart_tickets",
        null=True,
        blank=True,
    )
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")

    class Meta:
        db_table = "cart_tickets"


class Reservation(models.Model):
    reservation_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="reservations",
    )
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reservation"


class ReservationItem(models.Model):
    reservation_item_id = models.BigAutoField(primary_key=True)
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        db_column="reservation_id",
        related_name="items",
    )
    session = models.ForeignKey(
        EventSession,
        on_delete=models.CASCADE,
        db_column="session_id",
        related_name="reservation_items",
    )
    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.CASCADE,
        db_column="ticket_type_id",
        related_name="reservation_items",
    )
    seat = models.ForeignKey(
        Seat,
        on_delete=models.SET_NULL,
        db_column="seat_id",
        related_name="reservation_items",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "reservation_item"


class Order(models.Model):
    STATUS_AWAITING_PAYMENT = "awaiting_payment"
    STATUS_PAID = "paid"
    STATUS_CANCELLED = "cancelled"
    STATUS_REFUNDED = "refunded"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = [
        (STATUS_AWAITING_PAYMENT, "awaiting_payment"),
        (STATUS_PAID, "paid"),
        (STATUS_CANCELLED, "cancelled"),
        (STATUS_REFUNDED, "refunded"),
        (STATUS_EXPIRED, "expired"),
    ]

    order_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="orders",
    )
    cart = models.OneToOneField(
        Cart,
        on_delete=models.SET_NULL,
        db_column="cart_id",
        related_name="order",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_AWAITING_PAYMENT,
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "order"


class OrderTicket(models.Model):
    order_item_id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        db_column="order_id",
        related_name="order_tickets",
    )
    session = models.ForeignKey(
        EventSession,
        on_delete=models.CASCADE,
        db_column="session_id",
        related_name="order_tickets",
    )
    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.CASCADE,
        db_column="ticket_type_id",
        related_name="order_tickets",
    )
    seat = models.ForeignKey(
        Seat,
        on_delete=models.SET_NULL,
        db_column="seat_id",
        related_name="order_tickets",
        null=True,
        blank=True,
    )
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")

    class Meta:
        db_table = "order_ticket"


class Payment(models.Model):
    payment_id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        db_column="order_id",
        related_name="payments",
    )
    provider_payment_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "payment"


class Refund(models.Model):
    STATUS_REQUESTED = "requested"
    STATUS_APPROVED = "approved"
    STATUS_PROCESSING = "processing"
    STATUS_SUCCEEDED = "succeeded"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_REQUESTED, "requested"),
        (STATUS_APPROVED, "approved"),
        (STATUS_PROCESSING, "processing"),
        (STATUS_SUCCEEDED, "succeeded"),
        (STATUS_REJECTED, "rejected"),
    ]

    refund_id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        db_column="order_id",
        related_name="refunds",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REQUESTED)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "refund"


class UserPaymentMethod(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_DISABLED = "disabled"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "active"),
        (STATUS_DISABLED, "disabled"),
    ]

    payment_method_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="payment_methods",
    )
    provider_method_id = models.CharField(max_length=255)
    card_last4 = models.CharField(max_length=4, null=True, blank=True)
    card_brand = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    class Meta:
        db_table = "user_payment_method"
