


class OrderOrigin:
    CHECKOUT = "checkout"  # order created from checkout
    DRAFT = "draft"  # order created from draft order
    REISSUE = "reissue"  # order created from reissue existing one
    BULK_CREATE = "bulk_create"  # order created from bulk upload

    CHOICES = [
        (CHECKOUT, "Checkout"),
        (DRAFT, "Draft"),
        (REISSUE, "Reissue"),
        (BULK_CREATE, "Bulk create"),
    ]



class OrderStatus:
    DRAFT = "draft"  # fully editable, not finalized order created by staff users
    UNCONFIRMED = (
        "unconfirmed"  # order created by customers when confirmation is required
    )
    UNFULFILLED = "unfulfilled"  # order with no items marked as fulfilled
    PARTIALLY_FULFILLED = (
        "partially fulfilled"  # order with some items marked as fulfilled
    )
    FULFILLED = "fulfilled"  # order with all items marked as fulfilled

    PARTIALLY_RETURNED = (
        "partially_returned"  # order with some items marked as returned
    )
    RETURNED = "returned"  # order with all items marked as returned
    CANCELED = "canceled"  # permanently canceled order
    EXPIRED = "expired"  # order marked as expired

    CHOICES = [
        (DRAFT, "Draft"),
        (UNCONFIRMED, "Unconfirmed"),
        (UNFULFILLED, "Unfulfilled"),
        (PARTIALLY_FULFILLED, "Partially fulfilled"),
        (PARTIALLY_RETURNED, "Partially returned"),
        (RETURNED, "Returned"),
        (FULFILLED, "Fulfilled"),
        (CANCELED, "Canceled"),
        (EXPIRED, "Expired"),
    ]


ORDER_EDITABLE_STATUS = (OrderStatus.DRAFT, OrderStatus.UNCONFIRMED)



class OrderAuthorizeStatus:
    """Determine a current authorize status for order.

    We treat the order as fully authorized when the sum of authorized and charged funds
    cover the `order.total`-`order.totalGrantedRefund`.
    We treat the order as partially authorized when the sum of authorized and charged
    funds covers only part of the `order.total`-`order.totalGrantedRefund`.
    We treat the order as not authorized when the sum of authorized and charged funds is
    0.

    NONE - the funds are not authorized
    PARTIAL - the funds that are authorized and charged don't cover fully the
    `order.total`-`order.totalGrantedRefund`
    FULL - the funds that are authorized and charged fully cover the
    `order.total`-`order.totalGrantedRefund`
    """

    NONE = "none"
    PARTIAL = "partial"
    FULL = "full"

    CHOICES = [
        (NONE, "The funds are not authorized"),
        (
            PARTIAL,
            "The funds that are authorized and charged don't cover fully the order's "
            "total",
        ),
        (
            FULL,
            "The funds that are authorized and charged fully cover the order's total",
        ),
    ]



class OrderChargeStatus:
    """Determine the current charge status for the order.

    An order is considered overcharged when the sum of the
    transactionItem's charge amounts exceeds the value of
    `order.total` - `order.totalGrantedRefund`.
    If the sum of the transactionItem's charge amounts equals
    `order.total` - `order.totalGrantedRefund`, we consider the order to be fully
    charged.
    If the sum of the transactionItem's charge amounts covers a part of the
    `order.total` - `order.totalGrantedRefund`, we treat the order as partially charged.

    NONE - the funds are not charged.
    PARTIAL - the funds that are charged don't cover the
    `order.total`-`order.totalGrantedRefund`
    FULL - the funds that are charged fully cover the
    `order.total`-`order.totalGrantedRefund`
    OVERCHARGED - the charged funds are bigger than the
    `order.total`-`order.totalGrantedRefund`
    """

    NONE = "none"
    PARTIAL = "partial"
    FULL = "full"
    OVERCHARGED = "overcharged"

    CHOICES = [
        (NONE, "The order is not charged."),
        (PARTIAL, "The order is partially charged"),
        (FULL, "The order is fully charged"),
        (OVERCHARGED, "The order is overcharged"),
    ]

