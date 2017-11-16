import threading
import sys
import wmi
import helper
import pythoncom

class SensorUtils:
    _idlock = threading.Lock()
    _wmilock = threading.Lock()
    _wmi_dict = {}
    _cpu_sensor_ids = []
    _gpu_sensor_ids = []

    @staticmethod
    def initialize_thread():
        try:
            with SensorUtils._wmilock:
                if SensorUtils._get_wmi() is None:
                    pythoncom.CoInitialize()
                    SensorUtils._create_wmi()
        except:
            helper.show_error("OpenHardwareMonitor WMI data not found.\n\n"
                              "Please make sure that OpenHardwareMonitor is installed.\n\n"
                              "Latest version is available at:\n\n"
                              "http://openhardwaremonitor.org\n\n"
                              "The application will now exit.")
            sys.exit(0)

    @staticmethod
    def dispose_thread():
        SensorUtils._remove_wmi()
        pythoncom.CoUninitialize()

    @staticmethod
    def get_all_sensors():
        return SensorUtils._get_wmi().Sensor(["Name", "Parent", "Value", "Identifier"], SensorType="Temperature")

    @staticmethod
    def set_cpu_sensor_ids(ids):
        with SensorUtils._idlock:
            SensorUtils._cpu_sensor_ids = ids

    @staticmethod
    def set_gpu_sensor_ids(ids):
        with SensorUtils._idlock:
            SensorUtils._gpu_sensor_ids = ids

    @staticmethod
    def get_cpu_temp(calc="Max"):
        with SensorUtils._idlock:
            return SensorUtils._get_sensor_temp(SensorUtils.get_all_sensors(), SensorUtils._cpu_sensor_ids, calc)

    @staticmethod
    def get_gpu_temp(calc="Max"):
        with SensorUtils._idlock:
            return SensorUtils._get_sensor_temp(SensorUtils.get_all_sensors(), SensorUtils._gpu_sensor_ids, calc)

    @staticmethod
    def _get_sensor_temp(all_sensors, sensor_ids, calc):
        sensors = []
        for sensor in all_sensors:
            for sid in sensor_ids:
                if sid == sensor.Identifier:
                    sensors.append(sensor)

        if sensors:
            tmp = []
            for sensor in sensors:
                tmp.append(sensor.Value)
            temperatures = [float(t) for t in tmp]
        else:
            return 0

        if calc == "Max":
            return max(temperatures)
        elif calc == "Avg":
            return sum(temperatures) / len(temperatures)
        else:
            return 0

    @staticmethod
    def _get_wmi():
        threadid = threading.get_ident()
        return SensorUtils._wmi_dict[threadid] if threadid in SensorUtils._wmi_dict else None

    @staticmethod
    def _create_wmi():
        threadid = threading.get_ident()
        SensorUtils._wmi_dict[threadid] = wmi.WMI(namespace="root\OpenHardwareMonitor")

    @staticmethod
    def _remove_wmi():
        threadid = threading.get_ident()
        if threadid in SensorUtils._wmi_dict:
            del SensorUtils._wmi_dict[threadid]
