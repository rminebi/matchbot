# ConversationHandler states
(
    # Registration flow
    REG_NAME,
    REG_AGE,
    REG_GENDER,
    REG_CITY,
    REG_BIO,
    REG_PHOTO,
    REG_LOOKING_FOR,
    REG_AGE_RANGE,

    # Edit flow
    EDIT_FIELD,

    # Search settings
    SET_LOOKING_FOR,
    SET_AGE_MIN,
    SET_AGE_MAX,
) = range(12)
