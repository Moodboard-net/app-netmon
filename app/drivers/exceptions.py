class DeviceError(Exception):
    pass


class DeviceConnectionError(DeviceError):
    pass


class DeviceAuthError(DeviceError):
    pass


class DeviceTimeoutError(DeviceError):
    pass


class DeviceParseError(DeviceError):
    pass


class CapabilityNotSupported(DeviceError):
    pass
