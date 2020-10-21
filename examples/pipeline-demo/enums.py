import enum

class ProviderType(enum.Enum):
    satellite = 1
    drone = 2
    live_feed = 3


class visibilityType (enum.Enum):
    everyone = 1
    developerOnly = 2
    nobody = 3
