import ctypes
import ctypes.util
import platform
from typing import List, Optional, Tuple
import uuid

# Load the shared library
def load_sc5511a_library():
    lib_name = "sc5511a"
    if platform.system() == "Windows":
        lib_name = "sc5511a.dll"
    elif platform.system() == "Linux":
        lib_name = "libsc5511a.so"
    lib_path = ctypes.util.find_library(lib_name)
    if not lib_path:
        raise RuntimeError(f"Cannot find {lib_name} library")
    return ctypes.cdll.LoadLibrary(lib_path)

# Define structures from sc5511a.h
class DeviceInfoT(ctypes.Structure):
    class Date(ctypes.Structure):
        _fields_ = [
            ("year", ctypes.c_ubyte),
            ("month", ctypes.c_ubyte),
            ("day", ctypes.c_ubyte),
            ("hour", ctypes.c_ubyte),
        ]

    _fields_ = [
        ("product_serial_number", ctypes.c_uint),
        ("hardware_revision", ctypes.c_float),
        ("firmware_revision", ctypes.c_float),
        ("man_date", Date),
    ]

class ListModeT(ctypes.Structure):
    _fields_ = [
        ("sss_mode", ctypes.c_ubyte),
        ("sweep_dir", ctypes.c_ubyte),
        ("tri_waveform", ctypes.c_ubyte),
        ("hw_trigger", ctypes.c_ubyte),
        ("step_on_hw_trig", ctypes.c_ubyte),
        ("return_to_start", ctypes.c_ubyte),
        ("trig_out_enable", ctypes.c_ubyte),
        ("trig_out_on_cycle", ctypes.c_ubyte),
    ]

class PllStatusT(ctypes.Structure):
    _fields_ = [
        ("sum_pll_ld", ctypes.c_ubyte),
        ("crs_pll_ld", ctypes.c_ubyte),
        ("fine_pll_ld", ctypes.c_ubyte),
        ("crs_ref_pll_ld", ctypes.c_ubyte),
        ("crs_aux_pll_ld", ctypes.c_ubyte),
        ("ref_100_pll_ld", ctypes.c_ubyte),
        ("ref_10_pll_ld", ctypes.c_ubyte),
        ("rf2_pll_ld", ctypes.c_ubyte),
    ]

class OperateStatusT(ctypes.Structure):
    _fields_ = [
        ("rf1_lock_mode", ctypes.c_ubyte),
        ("rf1_loop_gain", ctypes.c_ubyte),
        ("device_access", ctypes.c_ubyte),
        ("rf2_standby", ctypes.c_ubyte),
        ("rf1_standby", ctypes.c_ubyte),
        ("auto_pwr_disable", ctypes.c_ubyte),
        ("alc_mode", ctypes.c_ubyte),
        ("rf1_out_enable", ctypes.c_ubyte),
        ("ext_ref_lock_enable", ctypes.c_ubyte),
        ("ext_ref_detect", ctypes.c_ubyte),
        ("ref_out_select", ctypes.c_ubyte),
        ("list_mode_running", ctypes.c_ubyte),
        ("rf1_mode", ctypes.c_ubyte),
        ("over_temp", ctypes.c_ubyte),
        ("harmonic_ss", ctypes.c_ubyte),
    ]

class DeviceStatusT(ctypes.Structure):
    _fields_ = [
        ("list_mode", ListModeT),
        ("operate_status", OperateStatusT),
        ("pll_status", PllStatusT),
    ]

class DeviceRfParamsT(ctypes.Structure):
    _fields_ = [
        ("rf1_freq", ctypes.c_ulonglong),
        ("start_freq", ctypes.c_ulonglong),
        ("stop_freq", ctypes.c_ulonglong),
        ("step_freq", ctypes.c_ulonglong),
        ("sweep_dwell_time", ctypes.c_uint),
        ("sweep_cycles", ctypes.c_uint),
        ("buffer_points", ctypes.c_uint),
        ("rf_level", ctypes.c_float),
        ("rf2_freq", ctypes.c_ushort),
    ]

class ClockConfigT(ctypes.Structure):
    _fields_ = [
        ("ext_ref_lock_enable", ctypes.c_ubyte),
        ("ref_out_select", ctypes.c_ubyte),
        ("ext_direct_clocking", ctypes.c_ubyte),
        ("ext_ref_freq", ctypes.c_ubyte),
    ]

class SC5511A:
    # Error codes from sc5511a.h
    SUCCESS = 0
    USBDEVICEERROR = -1
    USBTRANSFERERROR = -2
    INPUTNULL = -3
    COMMERROR = -4
    INPUTNOTALLOC = -5
    EEPROMOUTBOUNDS = -6
    INVALIDARGUMENT = -7
    INPUTOUTOFRANGE = -8
    NOREFWHENLOCK = -9
    NORESOURCEFOUND = -10
    INVALIDCOMMAND = -11

    def __init__(self, serial_number: Optional[str] = None):
        self.lib = load_sc5511a_library()
        self.handle = None
        self.serial_number = serial_number
        # Set up function prototypes
        self._setup_prototypes()

    def _setup_prototypes(self):
        """Configure ctypes function prototypes."""
        self.lib.sc5511a_search_devices.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
        self.lib.sc5511a_search_devices.restype = ctypes.c_int

        self.lib.sc5511a_open_device.argtypes = [ctypes.c_char_p]
        self.lib.sc5511a_open_device.restype = ctypes.c_void_p

        self.lib.sc5511a_close_device.argtypes = [ctypes.c_void_p]
        self.lib.sc5511a_close_device.restype = ctypes.c_int

        self.lib.sc5511a_set_rf_mode.argtypes = [ctypes.c_void_p, ctypes.c_ubyte]
        self.lib.sc5511a_set_rf_mode.restype = ctypes.c_int

        self.lib.sc5511a_set_freq.argtypes = [ctypes.c_void_p, ctypes.c_ulonglong]
        self.lib.sc5511a_set_freq.restype = ctypes.c_int

        self.lib.sc5511a_set_output.argtypes = [ctypes.c_void_p, ctypes.c_ubyte]
        self.lib.sc5511a_set_output.restype = ctypes.c_int

        self.lib.sc5511a_set_rf2_freq.argtypes = [ctypes.c_void_p, ctypes.c_ushort]
        self.lib.sc5511a_set_rf2_freq.restype = ctypes.c_int

        self.lib.sc5511a_set_level.argtypes = [ctypes.c_void_p, ctypes.c_float]
        self.lib.sc5511a_set_level.restype = ctypes.c_int

        self.lib.sc5511a_set_clock_reference.argtypes = [
            ctypes.c_void_p, ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte
        ]
        self.lib.sc5511a_set_clock_reference.restype = ctypes.c_int

        self.lib.sc5511a_get_temperature.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float)]
        self.lib.sc5511a_get_temperature.restype = ctypes.c_int

        self.lib.sc5511a_get_device_status.argtypes = [ctypes.c_void_p, ctypes.POINTER(DeviceStatusT)]
        self.lib.sc5511a_get_device_status.restype = ctypes.c_int

        self.lib.sc5511a_get_device_info.argtypes = [ctypes.c_void_p, ctypes.POINTER(DeviceInfoT)]
        self.lib.sc5511a_get_device_info.restype = ctypes.c_int

        self.lib.sc5511a_get_rf_parameters.argtypes = [ctypes.c_void_p, ctypes.POINTER(DeviceRfParamsT)]
        self.lib.sc5511a_get_rf_parameters.restype = ctypes.c_int

        self.lib.sc5511a_get_clock_config.argtypes = [ctypes.c_void_p, ctypes.POINTER(ClockConfigT)]
        self.lib.sc5511a_get_clock_config.restype = ctypes.c_int

        self.lib.sc5511a_reg_read.argtypes = [
            ctypes.c_void_p, ctypes.c_ubyte, ctypes.c_ulonglong, ctypes.POINTER(ctypes.c_ulonglong)
        ]
        self.lib.sc5511a_reg_read.restype = ctypes.c_int

        self.lib.sc5511a_reg_write.argtypes = [ctypes.c_void_p, ctypes.c_ubyte, ctypes.c_ulonglong]
        self.lib.sc5511a_reg_write.restype = ctypes.c_int

        self.lib.sc5511a_set_alc_mode.argtypes = [ctypes.c_void_p, ctypes.c_ubyte]
        self.lib.sc5511a_set_alc_mode.restype = ctypes.c_int

        self.lib.sc5511a_set_standby.argtypes = [ctypes.c_void_p, ctypes.c_ubyte]
        self.lib.sc5511a_set_standby.restype = ctypes.c_int

        self.lib.sc5511a_set_synth_mode.argtypes = [
            ctypes.c_void_p, ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte
        ]
        self.lib.sc5511a_set_synth_mode.restype = ctypes.c_int

        self.lib.sc5511a_set_signal_phase.argtypes = [ctypes.c_void_p, ctypes.c_float]
        self.lib.sc5511a_set_signal_phase.restype = ctypes.c_int

        self.lib.sc5511a_set_auto_level_disable.argtypes = [ctypes.c_void_p, ctypes.c_ubyte]
        self.lib.sc5511a_set_auto_level_disable.restype = ctypes.c_int

        self.lib.sc5511a_set_reference_dac.argtypes = [ctypes.c_void_p, ctypes.c_ushort]
        self.lib.sc5511a_set_reference_dac.restype = ctypes.c_int

        self.lib.sc5511a_set_alc_dac.argtypes = [ctypes.c_void_p, ctypes.c_ushort]
        self.lib.sc5511a_set_alc_dac.restype = ctypes.c_int

        self.lib.sc5511a_store_default_state.argtypes = [ctypes.c_void_p]
        self.lib.sc5511a_store_default_state.restype = ctypes.c_int

        self.lib.sc5511a_set_rf2_standby.argtypes = [ctypes.c_void_p, ctypes.c_ubyte]
        self.lib.sc5511a_set_rf2_standby.restype = ctypes.c_int

        self.lib.sc5511a_synth_self_cal.argtypes = [ctypes.c_void_p]
        self.lib.sc5511a_synth_self_cal.restype = ctypes.c_int

        self.lib.sc5511a_list_mode_config.argtypes = [ctypes.c_void_p, ctypes.POINTER(ListModeT)]
        self.lib.sc5511a_list_mode_config.restype = ctypes.c_int

        self.lib.sc5511a_list_start_freq.argtypes = [ctypes.c_void_p, ctypes.c_ulonglong]
        self.lib.sc5511a_list_start_freq.restype = ctypes.c_int

        self.lib.sc5511a_list_stop_freq.argtypes = [ctypes.c_void_p, ctypes.c_ulonglong]
        self.lib.sc5511a_list_stop_freq.restype = ctypes.c_int

        self.lib.sc5511a_list_step_freq.argtypes = [ctypes.c_void_p, ctypes.c_ulonglong]
        self.lib.sc5511a_list_step_freq.restype = ctypes.c_int

        self.lib.sc5511a_list_dwell_time.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        self.lib.sc5511a_list_dwell_time.restype = ctypes.c_int

        self.lib.sc5511a_list_cycle_count.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        self.lib.sc5511a_list_cycle_count.restype = ctypes.c_int

        self.lib.sc5511a_list_buffer_points.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        self.lib.sc5511a_list_buffer_points.restype = ctypes.c_int

        self.lib.sc5511a_list_buffer_write.argtypes = [ctypes.c_void_p, ctypes.c_ulonglong]
        self.lib.sc5511a_list_buffer_write.restype = ctypes.c_int

        self.lib.sc5511a_list_buffer_transfer.argtypes = [ctypes.c_void_p, ctypes.c_ubyte]
        self.lib.sc5511a_list_buffer_transfer.restype = ctypes.c_int

        self.lib.sc5511a_list_soft_trigger.argtypes = [ctypes.c_void_p]
        self.lib.sc5511a_list_soft_trigger.restype = ctypes.c_int

        self.lib.sc5511a_list_buffer_read.argtypes = [
            ctypes.c_void_p, ctypes.c_uint, ctypes.POINTER(ctypes.c_ulonglong)
        ]
        self.lib.sc5511a_list_buffer_read.restype = ctypes.c_int

        self.lib.sc5511a_get_alc_dac.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ushort)]
        self.lib.sc5511a_get_alc_dac.restype = ctypes.c_int

        self.lib.sc5511a_get_signal_phase.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float)]
        self.lib.sc5511a_get_signal_phase.restype = ctypes.c_int

    def __enter__(self):
        """Context manager enter."""
        if self.serial_number:
            self.open_device(self.serial_number)
        else:
            devices = self.search_devices()
            if not devices:
                raise RuntimeError("No SC5511A devices found")
            self.open_device(devices[0])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit, ensure device is closed."""
        self.close_device()

    def search_devices(self) -> List[str]:
        """Search for connected SC5511A devices and return their serial numbers."""
        MAXDEVICES = 50
        SCI_SN_LENGTH = 8
        device_list = (ctypes.POINTER(ctypes.c_char) * MAXDEVICES)()
        for i in range(MAXDEVICES):
            device_list[i] = (ctypes.c_char * SCI_SN_LENGTH)()
        
        num_devices = self.lib.sc5511a_search_devices(device_list)
        if num_devices <= 0:
            return []
        
        return [ctypes.string_at(device_list[i], SCI_SN_LENGTH).decode('utf-8').strip() for i in range(num_devices)]

    def open_device(self, serial_number: str) -> None:
        """Open a device by its serial number."""
        serial_c = ctypes.c_char_p(serial_number.encode('utf-8'))
        self.handle = self.lib.sc5511a_open_device(serial_c)
        if not self.handle:
            raise RuntimeError(f"Failed to open device with serial number {serial_number}")

    def close_device(self) -> None:
        """Close the device and free resources."""
        if self.handle:
            status = self.lib.sc5511a_close_device(self.handle)
            if status != self.SUCCESS:
                raise RuntimeError(f"Failed to close device: error code {status}")
            self.handle = None

    def set_rf_mode(self, mode: int) -> None:
        """Set RF mode (0: single tone, 1: sweep/list)."""
        status = self.lib.sc5511a_set_rf_mode(self.handle, mode)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set RF mode: error code {status}")

    def set_freq(self, freq: int) -> None:
        """Set RF1 frequency in Hz."""
        status = self.lib.sc5511a_set_freq(self.handle, freq)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set frequency: error code {status}")

    def set_output(self, enable: bool) -> None:
        """Enable or disable RF1 output."""
        status = self.lib.sc5511a_set_output(self.handle, 1 if enable else 0)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set output: error code {status}")

    def set_rf2_freq(self, freq: int) -> None:
        """Set RF2 frequency in MHz."""
        status = self.lib.sc5511a_set_rf2_freq(self.handle, freq)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set RF2 frequency: error code {status}")

    def set_level(self, power_level: float) -> None:
        """Set RF1 power level in dBm."""
        status = self.lib.sc5511a_set_level(self.handle, power_level)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set power level: error code {status}")

    def set_clock_reference(self, ext_ref_freq: int, ext_direct_clk: int, select_high: int, lock_external: int) -> None:
        """Set clock reference parameters."""
        status = self.lib.sc5511a_set_clock_reference(
            self.handle, ext_ref_freq, ext_direct_clk, select_high, lock_external
        )
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set clock reference: error code {status}")

    def get_clock_config(self) -> ClockConfigT:
        """Get clock configuration."""
        config = ClockConfigT()
        status = self.lib.sc5511a_get_clock_config(self.handle, ctypes.byref(config))
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to get clock config: error code {status}")
        return config

    def get_temperature(self) -> float:
        """Get device temperature in Celsius."""
        temp = ctypes.c_float()
        status = self.lib.sc5511a_get_temperature(self.handle, ctypes.byref(temp))
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to get temperature: error code {status}")
        return temp.value

    def get_device_status(self) -> DeviceStatusT:
        """Get device status."""
        status_struct = DeviceStatusT()
        status = self.lib.sc5511a_get_device_status(self.handle, ctypes.byref(status_struct))
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to get device status: error code {status}")
        return status_struct

    def get_device_info(self) -> DeviceInfoT:
        """Get device information."""
        info = DeviceInfoT()
        status = self.lib.sc5511a_get_device_info(self.handle, ctypes.byref(info))
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to get device info: error code {status}")
        return info

    def get_rf_parameters(self) -> DeviceRfParamsT:
        """Get RF parameters."""
        params = DeviceRfParamsT()
        status = self.lib.sc5511a_get_rf_parameters(self.handle, ctypes.byref(params))
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to get RF parameters: error code {status}")
        return params

    def reg_read(self, reg_byte: int, instruct_word: int) -> int:
        """Read a register value."""
        received_word = ctypes.c_ulonglong()
        status = self.lib.sc5511a_reg_read(
            self.handle, reg_byte, instruct_word, ctypes.byref(received_word)
        )
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to read register: error code {status}")
        return received_word.value

    def reg_write(self, reg_byte: int, instruct_word: int) -> None:
        """Write to a register."""
        status = self.lib.sc5511a_reg_write(self.handle, reg_byte, instruct_word)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to write register: error code {status}")

    def set_alc_mode(self, mode: int) -> None:
        """Set ALC mode."""
        status = self.lib.sc5511a_set_alc_mode(self.handle, mode)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set ALC mode: error code {status}")

    def set_standby(self, enable: bool) -> None:
        """Set standby mode."""
        status = self.lib.sc5511a_set_standby(self.handle, 1 if enable else 0)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set standby: error code {status}")

    def set_synth_mode(self, disable_spur_suppress: int, low_loop_gain: int, lock_mode: int) -> None:
        """Set synthesizer mode."""
        status = self.lib.sc5511a_set_synth_mode(
            self.handle, disable_spur_suppress, low_loop_gain, lock_mode
        )
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set synth mode: error code {status}")

    def set_signal_phase(self, phase: float) -> None:
        """Set signal phase."""
        status = self.lib.sc5511a_set_signal_phase(self.handle, phase)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set signal phase: error code {status}")

    def set_auto_level_disable(self, disable: bool) -> None:
        """Set auto level disable."""
        status = self.lib.sc5511a_set_auto_level_disable(self.handle, 1 if disable else 0)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set auto level disable: error code {status}")

    def set_reference_dac(self, dac_value: int) -> None:
        """Set reference DAC."""
        status = self.lib.sc5511a_set_reference_dac(self.handle, dac_value)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set reference DAC: error code {status}")

    def set_alc_dac(self, dac_value: int) -> None:
        """Set ALC DAC."""
        status = self.lib.sc5511a_set_alc_dac(self.handle, dac_value)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set ALC DAC: error code {status}")

    def store_default_state(self) -> None:
        """Store default state."""
        status = self.lib.sc5511a_store_default_state(self.handle)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to store default state: error code {status}")

    def set_rf2_standby(self, enable: bool) -> None:
        """Set RF2 standby."""
        status = self.lib.sc5511a_set_rf2_standby(self.handle, 1 if enable else 0)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set RF2 standby: error code {status}")

    def synth_self_cal(self) -> None:
        """Perform synthesizer self-calibration."""
        status = self.lib.sc5511a_synth_self_cal(self.handle)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to perform synth self-cal: error code {status}")

    def list_mode_config(self, list_mode: ListModeT) -> None:
        """Configure list mode."""
        status = self.lib.sc5511a_list_mode_config(self.handle, ctypes.byref(list_mode))
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to configure list mode: error code {status}")

    def list_start_freq(self, freq: int) -> None:
        """Set list start frequency."""
        status = self.lib.sc5511a_list_start_freq(self.handle, freq)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set list start frequency: error code {status}")

    def list_stop_freq(self, freq: int) -> None:
        """Set list stop frequency."""
        status = self.lib.sc5511a_list_stop_freq(self.handle, freq)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set list stop frequency: error code {status}")

    def list_step_freq(self, freq: int) -> None:
        """Set list step frequency."""
        status = self.lib.sc5511a_list_step_freq(self.handle, freq)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set list step frequency: error code {status}")

    def list_dwell_time(self, dwell_time: int) -> None:
        """Set list dwell time."""
        status = self.lib.sc5511a_list_dwell_time(self.handle, dwell_time)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set dwell time: error code {status}")

    def list_cycle_count(self, cycle_count: int) -> None:
        """Set list cycle count."""
        status = self.lib.sc5511a_list_cycle_count(self.handle, cycle_count)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set cycle count: error code {status}")

    def list_buffer_points(self, list_points: int) -> None:
        """Set list buffer points."""
        status = self.lib.sc5511a_list_buffer_points(self.handle, list_points)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to set buffer points: error code {status}")

    def list_buffer_write(self, freq: int) -> None:
        """Write to list buffer."""
        status = self.lib.sc5511a_list_buffer_write(self.handle, freq)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to write list buffer: error code {status}")

    def list_buffer_transfer(self, transfer_mode: int) -> int:
        """Transfer list buffer."""
        status = self.lib.sc5511a_list_buffer_transfer(self.handle, transfer_mode)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to transfer list buffer: error code {status}")
        return status

    def list_soft_trigger(self) -> None:
        """Trigger list mode."""
        status = self.lib.sc5511a_list_soft_trigger(self.handle)
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to trigger list: error code {status}")

    def list_buffer_read(self, address: int) -> int:
        """Read from list buffer."""
        freq = ctypes.c_ulonglong()
        status = self.lib.sc5511a_list_buffer_read(self.handle, address, ctypes.byref(freq))
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to read list buffer: error code {status}")
        return freq.value

    def get_alc_dac(self) -> int:
        """Get ALC DAC value."""
        dac_value = ctypes.c_ushort()
        status = self.lib.sc5511a_get_alc_dac(self.handle, ctypes.byref(dac_value))
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to get ALC DAC: error code {status}")
        return dac_value.value

    def get_signal_phase(self) -> float:
        """Get signal phase."""
        phase = ctypes.c_float()
        status = self.lib.sc5511a_get_signal_phase(self.handle, ctypes.byref(phase))
        if status != self.SUCCESS:
            raise RuntimeError(f"Failed to get signal phase: error code {status}")
        return phase.value
    
    def __enter__(self):
        """Context manager enter."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit, ensure device is closed."""
        self.close_device()