from itertools import chain

GenderChoices = (
    ("male", "Male"),
    ("female", "Female"),
    ("other", "Other"),
)

GIRLS = 'girls'
BOYS = 'boys'
FAMILY = 'family'

APARTMENT = 'apartment'
INDEPENDENT = 'independent'
VILLA = 'villa'

HouseTypeCategories = (
    (APARTMENT, 'Apartment'),
    (INDEPENDENT, 'Independent House'),
    (VILLA, 'Villa'),
)

FULLY_FURNISHED = 'full'
SEMI_FURNISHED = 'semi'
UNFURNISHED = 'nil'

HouseFurnishTypeCategories = (
    (FULLY_FURNISHED, 'Fully furnished'),
    (SEMI_FURNISHED, 'Semi furnished'),
    (UNFURNISHED, 'Unfurnished')
)

HouseAccomodationAllowedCategories = (
    (GIRLS, 'Girls'),
    (BOYS, 'Boys'),
    (FAMILY, 'Family')
)

FLAT = 'flat'
PRIVATE_ROOM = 'private'
SHARED_ROOM = 'shared'

HouseSpaceTypeCategories = (
    (SHARED_ROOM, 'Shared rooms'),
    (PRIVATE_ROOM, 'Private rooms'),
    (FLAT, 'Entire house'),
)

SPACE_SUBTYPES = {
    SHARED_ROOM: ['1-Bed Sharing', '2-Bed Sharing', '3-Bed Sharing'],
    PRIVATE_ROOM: ['1-BHK', '2-BHK', '3-BHK'],
    FLAT: ['1-BHK', '2-BHK', '3-BHK']
}

SPACE_SUBTYPES_LIST = list(chain(*SPACE_SUBTYPES.values()))

HouseSpaceSubTypeCategories = list(zip(SPACE_SUBTYPES_LIST, SPACE_SUBTYPES_LIST))

HouseCurrentStayStatusCategories = (
    ("I'm staying", "I'm staying"),
    ("Tenant is staying", "Tenant is staying"),
    ("It's vacant", "It's vacant"),
)