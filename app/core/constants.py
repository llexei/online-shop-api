STAFF_ROLES = {"admin", "manager"}


ALLOWED_STATUS = {
    "pending": {"assembled", "cancelled"},
    "assembled": {"shipped", "cancelled"},
    "shipped": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
}


ALLOWED_ROLES=['user','manager','admin']