from typing import List

import allure
import pytest
from time import sleep

from meter_interaction.itep_mock import ItepMock

from support.hydrus2.commands import disable_ultrasonic_simulation, reset_volume_accus, set_us_measurement_rate, \
    start_high_resolution_test, stop_high_resolution_test
from support.data_parser import reverse_stream
from support.error_handler import get_active_errors, get_error_state
from support.hydrus2.communication import send_command
from support.meter_types import ErrorClass, ErrorMask, MeterOperation, MeterMode, UltrasonicSimulationMode, \
    OperationMode, MeasurementRate, MeterType, PulseOutputMode

# **********************************
# Global parameters and dictionaries
# **********************************

MEASURMENT_UNITS_IRDA = {
    'KILO_LITERS': '00',
    'CUBIC_METERS': '01',
    'CUBIC_FEET': '02',
    'US_GALLONS': '03',
    'IMPERIAL_GALLONS': '04'
}
PULSE_VALUES = {
    '1': '10 27 00 00',
    '10': 'A0 86 01 00',
    '20': '40 0D 03 00',
    '50': '20 A1 07 00',
    '100': '40 42 0F 00'
}
CHANNEL_TYPE_BURST = {
    'positive': '04',
    'negative': '05',
    'absolute': '06',
    'bothWithSign': '07',
    'sign': '08',
    'off': '00'
}
CHANNEL_TYPE_TCP = {
    'positive': '01',
    'negative': '02',
    'sum': '03',
    'errors': '09',
    'off': '00'
}
# 1365 - HALF TICKS in 12Hz
HALFPERIODE_IN_TICK_12HZ = '55 05'
# 4098 - HALF TICKS in 4Hz
HALFPERIODE_IN_TICK_4HZ = '02 10'
HALFPERIODE_IN_TICK = {'4': HALFPERIODE_IN_TICK_4HZ, '12': HALFPERIODE_IN_TICK_12HZ}
SIMULATION_PHASE_DIFF_18Q3 = {
    'Q1': 6400,
    'Q2': 10240,
    'Q3': 5120000,
    'Q4': 6400000,
    '2Q4': 12800000}
# '00 E0 B1 FF'
SIMULATION_PHASE_DIFF_18Q3_NEGATIVE = 4289847296
SIMULATION_PHASE_DIFF_2_5Q3 = {
    'Q1': 890,
    'Q2': 1423,
    'Q3': 711680,
    'Q4': 889600,
    '2Q4': 1779200}
SIMULATION_PHASE_DIFF = {'2_5': SIMULATION_PHASE_DIFF_2_5Q3, '18': SIMULATION_PHASE_DIFF_18Q3}
TIME_12HZ_18Q3 = {
    'Q1': 3600,
    'Q2': 3600,
    'Q3': 87,
    'Q4': 70,
    '2Q4': 35}

TIME_4HZ_18Q3 = {
    'Q1': 3600,
    'Q2': 3600,
    'Q3': 30,
    'Q4': 27,
    '2Q4': 13}

TIME_12HZ_2_5Q3 = {
    'Q1': 3600,
    'Q2': 3600,
    'Q3': 623,
    'Q4': 497,
    '2Q4': 249}

TIME_4HZ_2_5Q3 = {
    'Q1': 3600,
    'Q2': 3600,
    'Q3': 208,
    'Q4': 166,
    '2Q4': 83}
TIME4HZ = {'2_5': TIME_4HZ_2_5Q3, '18': TIME_4HZ_18Q3}
TIME12HZ = {'2_5': TIME_12HZ_2_5Q3, '18': TIME_12HZ_18Q3}
TIME = {'4': TIME4HZ, '12': TIME12HZ}
VOLUME_MULTIPLIER = {'bulk': 5, 'domestic': 6}
Q3_RANGE = {'2_5': '1', '18': '10'}
CONFIG_Q3_1 = {
    'SetFlowMeasurementCharacteristicMap1':
        '356E 356E 356E 356E 356E 356E 356E 356E 356E 356E 356E 356E 356E 356E ' +
        '356E 356E 356E 356E 356E 356E 356E 356E 356E 356E 356E 0000 0000 0000 ' +
        '0000 0000 B468 B468 B468 B468 B468 B468 B468 B468 B468 B468 B468 B468 ' +
        'B468 B468 B468 B468 B468 B468 B468 B468 B468 B468 B468 B468 64' +
        'B468 0000 0000 0000 0000 0000 2464 2464 2464 2464 2464 2464 2464 2464 ' +
        '2464 2464 2464 2464 2464 2464 2464 2464 2464 2464 2464 2464 2464 2464 ' +
        '2464 2464 2464 0000 0000 0000 0000 0000 5B60 5B60 5B60 5B60 5B60 5B60 ' +
        '5B60 5B60 5B60 5B60 5B60 5B60 5B60 5B60',
    'SetFlowMeasurementCharacteristicMap2':
        '5B60 5B60 5B60 5B60 5B60 5B60 5B60 5B60 5B60 5B60 5B60 0000 0000 0000 ' +
        '0000 0000 365D 365D 365D 365D 365D 365D 365D 365D 365D 365D 365D 365D ' +
        '365D 365D 365D 365D 365D 365D 365D 365D 365D 365D 365D 365D 365D 0000 ' +
        '0000 0000 0000 0000 A05A A05A A05A A05A A05A A05A A05A A05A 64 ' +
        'A05A A05A A05A A05A A05A A05A A05A A05A A05A A05A A05A A05A A05A A05A ' +
        'A05A A05A A05A 0000 0000 0000 0000 0000 7F58 7F58 7F58 7F58 7F58 7F58 ' +
        '7F58 7F58 7F58 7F58 7F58 7F58 7F58 7F58 7F58 7F58 7F58 7F58 7F58 7F58 ' +
        '7F58 7F58 7F58 7F58 7F58 0000 0000 0000',
    'SetFlowMeasurementCharacteristicMap3':
        '0000 0000 C456 C456 C456 C456 C456 C456 C456 C456 C456 C456 C456 C456 ' +
        'C456 C456 C456 C456 C456 C456 C456 C456 C456 C456 C456 C456 C456 0000 ' +
        '0000 0000 0000 0000 6655 6655 6655 6655 6655 6655 6655 6655 6655 6655 ' +
        '6655 6655 6655 6655 6655 6655 6655 6655 6655 6655 6655 6655 64 ' +
        '6655 6655 6655 0000 0000 0000 0000 0000 5554 5554 5554 5554 5554 5554 ' +
        '5554 5554 5554 5554 5554 5554 5554 5554 5554 5554 5554 5554 5554 5554 ' +
        '5554 5554 5554 5554 5554 0000 0000 0000 0000 0000 8D53 8D53 8D53 8D53 ' +
        '8D53 8D53 8D53 8D53 8D53 8D53 8D53 8D53',
    'SetFlowMeasurementCharacteristicMap4':
        '8D53 8D53 8D53 8D53 8D53 8D53 8D53 8D53 8D53 8D53 8D53 8D53 8D53 0000 ' +
        '0000 0000 0000 0000 0753 0753 0753 0753 0753 0753 0753 0753 0753 0753 ' +
        '0753 0753 0753 0753 0753 0753 0753 0753 0753 0753 0753 0753 0753 0753 ' +
        '0753 0000 0000 0000 0000 0000 BB52 BB52 BB52 BB52 BB52 BB52 64 ' +
        'BB52 BB52 BB52 BB52 BB52 BB52 BB52 BB52 BB52 BB52 BB52 BB52 BB52 BB52 ' +
        'BB52 BB52 BB52 BB52 BB52 0000 0000 0000 0000 0000 0000 0000 0000 0000 ' +
        '0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 ' +
        '0000 0000 0000 0000 0000 0000 0000 0000',
    'Set_ldacm_data_usMeasurementTemperatureSamplingPoints':
        '6400 9600 C800 FA00 2C01 5E01 9001 C201 F401 2602 5802 8A02 BC02 0000',
    'Set_ldacm_data_usMeasurementMeasurementEffectSamplingPoints':
        'C4200000 671F1000 091E2000 AC1C3000 4E1B4000 F0195000 93186000 35177000 ' +
        'D8158000 7A149000 1D13A000 BF11B000 6210C000 040FD000 A70DE000 490CF000 ' +
        'EC0A0001 8E091001 31082001 D3063001 76054001 18045001 BB026001 5D017001 ' +
        '00008001 00000000 00000000 00000000 00000000 00000000',
    'Set_ldacm_data_usMeasurementFracBitsCharacteristicMap': '04',
    'Set_ldacm_data_usMeasurementFracBitsVolumeIncrement': '10',
    'Set_ldacm_data_usMeasurementCharacteristicMapUnit': '00',
    'Set_ldacm_data_volumeDefinitionsHysteresis_positivBorder': 'E803',
    'Set_nldacm_data_volumeTestOpticalPulseValue': '10270000',
    'Set_ldacm_data_selfDisclosure_flowRateQ3': '1000'
}
FREQUENCY_BURST = {
    '4Hz': '00',
    '12Hz': '01',
}
PULSE_OUTPUT = {
    'output1': '1',
    'output2': '2',
    'both': '3'
}
PULSE_CHANNEL = {
    'output1': '00',
    'output2': '01'
}

CONFIG_Q3_10 = {
    'SetFlowMeasurementCharacteristicMap1':
        '356E 356E 356E 356E 356E 356E 356E 356E 356E 356E 356E 356E 356E 356E ' +
        '356E 356E 356E 356E 356E 356E 356E 356E 356E 356E 356E 0000 0000 0000 ' +
        '0000 0000 B468 B468 B468 B468 B468 B468 B468 B468 B468 B468 B468 B468 ' +
        'B468 B468 B468 B468 B468 B468 B468 B468 B468 B468 B468 B468 64' +
        'B468 0000 0000 0000 0000 0000 2464 2464 2464 2464 2464 2464 2464 2464 ' +
        '2464 2464 2464 2464 2464 2464 2464 2464 2464 2464 2464 2464 2464 2464 ' +
        '2464 2464 2464 0000 0000 0000 0000 0000 5B60 5B60 5B60 5B60 5B60 5B60 ' +
        '5B60 5B60 5B60 5B60 5B60 5B60 5B60 5B60',
    'SetFlowMeasurementCharacteristicMap2':
        '5B60 5B60 5B60 5B60 5B60 5B60 5B60 5B60 5B60 5B60 5B60 0000 0000 0000 ' +
        '0000 0000 365D 365D 365D 365D 365D 365D 365D 365D 365D 365D 365D 365D ' +
        '365D 365D 365D 365D 365D 365D 365D 365D 365D 365D 365D 365D 365D 0000 ' +
        '0000 0000 0000 0000 A05A A05A A05A A05A A05A A05A A05A A05A 64 ' +
        'A05A A05A A05A A05A A05A A05A A05A A05A A05A A05A A05A A05A A05A A05A ' +
        'A05A A05A A05A 0000 0000 0000 0000 0000 7F58 7F58 7F58 7F58 7F58 7F58 ' +
        '7F58 7F58 7F58 7F58 7F58 7F58 7F58 7F58 7F58 7F58 7F58 7F58 7F58 7F58 ' +
        '7F58 7F58 7F58 7F58 7F58 0000 0000 0000',
    'SetFlowMeasurementCharacteristicMap3':
        '0000 0000 C456 C456 C456 C456 C456 C456 C456 C456 C456 C456 C456 C456 ' +
        'C456 C456 C456 C456 C456 C456 C456 C456 C456 C456 C456 C456 C456 0000 ' +
        '0000 0000 0000 0000 6655 6655 6655 6655 6655 6655 6655 6655 6655 6655 ' +
        '6655 6655 6655 6655 6655 6655 6655 6655 6655 6655 6655 6655 64 ' +
        '6655 6655 6655 0000 0000 0000 0000 0000 5554 5554 5554 5554 5554 5554 ' +
        '5554 5554 5554 5554 5554 5554 5554 5554 5554 5554 5554 5554 5554 5554 ' +
        '5554 5554 5554 5554 5554 0000 0000 0000 0000 0000 8D53 8D53 8D53 8D53 ' +
        '8D53 8D53 8D53 8D53 8D53 8D53 8D53 8D53',
    'SetFlowMeasurementCharacteristicMap4':
        '8D53 8D53 8D53 8D53 8D53 8D53 8D53 8D53 8D53 8D53 8D53 8D53 8D53 0000 ' +
        '0000 0000 0000 0000 0753 0753 0753 0753 0753 0753 0753 0753 0753 0753 ' +
        '0753 0753 0753 0753 0753 0753 0753 0753 0753 0753 0753 0753 0753 0753 ' +
        '0753 0000 0000 0000 0000 0000 BB52 BB52 BB52 BB52 BB52 BB52 64 ' +
        'BB52 BB52 BB52 BB52 BB52 BB52 BB52 BB52 BB52 BB52 BB52 BB52 BB52 BB52 ' +
        'BB52 BB52 BB52 BB52 BB52 0000 0000 0000 0000 0000 0000 0000 0000 0000 ' +
        '0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 ' +
        '0000 0000 0000 0000 0000 0000 0000 0000',
    'Set_ldacm_data_usMeasurementTemperatureSamplingPoints':
        '6400 9600 C800 FA00 2C01 5E01 9001 C201 F401 2602 5802 8A02 BC02 0000',
    'Set_ldacm_data_usMeasurementMeasurementEffectSamplingPoints':
        'C4200000 671F1000 091E2000 AC1C3000 4E1B4000 F0195000 93186000 35177000 ' +
        'D8158000 7A149000 1D13A000 BF11B000 6210C000 040FD000 A70DE000 490CF000 ' +
        'EC0A0001 8E091001 31082001 D3063001 76054001 18045001 BB026001 5D017001 ' +
        '00008001 00000000 00000000 00000000 00000000 00000000',
    'Set_ldacm_data_usMeasurementFracBitsCharacteristicMap': '04',
    'Set_ldacm_data_usMeasurementFracBitsVolumeIncrement': '10',
    'Set_ldacm_data_usMeasurementCharacteristicMapUnit': '01',
    'Set_ldacm_data_volumeDefinitionsHysteresis_positivBorder': 'E803',
    'Set_nldacm_data_volumeTestOpticalPulseValue': '10270000',
    'Set_ldacm_data_selfDisclosure_flowRateQ3': '6400'
}

PULSEBOX_CHANNEL = {
    'output1': '0',
    'output2': '1'
}
PULSE_LEVEL = {
    'active': '01',
    'inactive': '00'
}
ACCU_TYPE = {
    'positive': 1,
    'negative': 2,
    'sum': 0,
    'absolute': 0,
    'bothWithSign': 0
}

PULSE_VALUE20 = '40 0D 03 00'  # 200000
MIN_HALF_PERIODE = '66 06'  # 1638 (from parameters.txt)
MIN_HALF_PERIODE_GOOD = '7A 06'  # 1658
MIN_HALF_PERIODE_BAD = '52 06'  # 1618
MIN_HALF_PERIODE_4HZ = '00 10'  # 4096
MIN_HALF_PERIODE_12HZ = '55 05'  # 1365
MAX_ACTIVE_TIME = '00 40'  # 16384 (from parameters.txt)
MAX_ACTIVE_TIME_GOOD = '38 3F'  # 16184
MAX_ACTIVE_TIME_BAD = 'C8 40'  # 16584
MAX_ACTIVE_TIME_4HZ = '00 10'  # 4096
MAX_ACTIVE_TIME_12HZ = '55 05'  # 1365
CONFIG_Q3 = {'1': CONFIG_Q3_1, '10': CONFIG_Q3_10}
CONFIGURATION_COMMANDS = [
    'SetFlowMeasurementCharacteristicMap1',
    'SetFlowMeasurementCharacteristicMap2',
    'SetFlowMeasurementCharacteristicMap3',
    'SetFlowMeasurementCharacteristicMap4',
    'Set_ldacm_data_usMeasurementTemperatureSamplingPoints',
    'Set_ldacm_data_usMeasurementMeasurementEffectSamplingPoints',
    'Set_ldacm_data_usMeasurementFracBitsCharacteristicMap',
    'Set_ldacm_data_usMeasurementFracBitsVolumeIncrement',
    'Set_ldacm_data_usMeasurementCharacteristicMapUnit',
    'Set_ldacm_data_volumeDefinitionsHysteresis_positivBorder',
    'Set_nldacm_data_volumeTestOpticalPulseValue',
    'Set_ldacm_data_selfDisclosure_flowRateQ3'
]

MAP_UNIT_VALUE = {
    '00': 1,
    '01': 10,
    '02': 100,
    '03': 1000
}
CFG_COMMANDS_MAIN = [
    'Get_ldacm_data_pulseOutput_maxValueOf_maxActiveTime_inTicks',
    'Get_ldacm_data_pulseOutput_minValueOf_minHalfPeriode_inTicks',
    'Get_ldacm_data_pulseOutput_maxValueOf_minHalfPeriode_inTicks_optical',
]
CFG_COMMANDS_PER_CHANNEL = [
    'Get_ldacm_data_pulseOutput_channelType_###',
    'Get_ldacm_data_pulseOutput_errorClass_###',
    'Get_ldacm_data_pulseOutput_pulseValue_###',
    'Get_ldacm_data_pulseOutput_minHalfPeriode_inTicks_###',
    'Get_ldacm_data_pulseOutput_maxActiveTime_inTicks_###',
    'Get_ldacm_data_pulseOutput_errorMask_###'
]
NUM_CHANNELS_SHARKY = 3


# **********************************
# Local Functions
# **********************************
def get_pulses_info(init: ItepMock, channels: int = 2) -> dict:
    pulses_info = {}
    for command in CFG_COMMANDS_MAIN:
        ret_param = command.replace("Get_", "")
        pulses_info[command] = send_command(init, command, return_parameters=[ret_param])[ret_param]
    for cmd in CFG_COMMANDS_PER_CHANNEL:
        for i in range(1, channels + 1):
            cmd_for_channel = cmd.replace("###", str(i))
            ret_param = cmd_for_channel.replace("Get_", "")
            pulses_info[cmd_for_channel] = send_command(init, cmd_for_channel, return_parameters=[ret_param])[ret_param]
    return pulses_info


def write_and_verify(init, command, input_value):
    send_command(init, f'Set_{command}', input_value)
    value_in_meter = send_command(init, f'Get_{command}', return_parameters=[command])[command]
    if input_value != value_in_meter:
        raise Exception(f'''Parameter: "{input_value}" was not written by command: "{command}".
                            Value in meter is: "{value_in_meter}"''')


def create_multiplier(init) -> int:
    map_resolution = send_command(init, 'Get_ldacm_data_usMeasurementCharacteristicMapUnit',
                                  return_parameters=['ldacm_data_usMeasurementCharacteristicMapUnit'])[
        'ldacm_data_usMeasurementCharacteristicMapUnit']
    multiplier = {'00': 6, '01': 5, '02': 4, '03': 3}
    return multiplier[map_resolution]


def round_pulses_to_resolution(number, round_to, multiplier) -> int:
    # This function devides count by pulse resolution and rounds down
    rounded, _ = divmod(number * (10 ** multiplier), round_to)
    return rounded * round_to


def configure_meter_for_q3(init, q3):
    for i in CONFIGURATION_COMMANDS:
        send_command(init, i, CONFIG_Q3[q3][i])


def get_volume_definition(init, accu) -> int:
    volume = send_command(init, f'Get_ldacm_data_volumeDefinitionsAccu{ACCU_TYPE[accu]}',
                          return_parameters=[f'ldacm_data_volumeDefinitionsAccu{ACCU_TYPE[accu]}'])[
        f'ldacm_data_volumeDefinitionsAccu{ACCU_TYPE[accu]}']
    decimals = send_command(init, 'Get_ldacm_data_volumeDefinitionsDecimalPlace',
                            return_parameters=['ldacm_data_volumeDefinitionsDecimalPlace'])[
        'ldacm_data_volumeDefinitionsDecimalPlace']
    volume = int(reverse_stream(volume, False), 10) / (1 * 10 ** int(decimals, 16))
    return volume


def set_pulse_output_channel_type_time(init, channel, channel_type):
    command = f'ldacm_data_pulseOutput_channelType_{channel}'
    # Resetting volume accu by setting something different
    write_and_verify(init, command, CHANNEL_TYPE_TCP['off'])
    sleep(5)
    # Setting correct channelType
    write_and_verify(init, command, CHANNEL_TYPE_TCP[channel_type])


def set_pulse_output_channel_type_burst(init, channel, channel_type):
    command = f'ldacm_data_pulseOutput_channelType_{channel}'
    # Resetting volume accu by setting something different
    write_and_verify(init, command, CHANNEL_TYPE_BURST['off'])
    sleep(5)
    # Setting correct channelType
    write_and_verify(init, command, CHANNEL_TYPE_BURST[channel_type])


def volume_definitions_hysteresis_border(init, border_sign, input_value=None):  # sign is positiv or negativ
    write_and_verify(init, f'ldacm_data_volumeDefinitionsHysteresis_{border_sign}Border', input_value)


def set_pulse_value(init, arg, pulse_output='2'):
    write_and_verify(init, f'ldacm_data_pulseOutput_pulseValue_{pulse_output}', PULSE_VALUES[arg])


def set_level_output(init, output, level):
    send_command(init, 'TestPulseOutput', f'0{PULSE_OUTPUT[output]} {PULSE_LEVEL[level]}')


def set_error_class(init, channel, arg):
    write_and_verify(init, f'ldacm_data_pulseOutput_errorClass_{channel}', arg.value)


def get_meter_type(init):
    config_meter_type = \
        send_command(init, 'Get_nldacm_data_hardwareConfigMeterType',
                     return_parameters=['nldacm_data_hardwareConfigMeterType'])['nldacm_data_hardwareConfigMeterType']
    bits = int(reverse_stream(config_meter_type, False), 16)
    # Size inform in 8 bit
    # 0 -> domestic, 1 (value - 256) -> bulk
    if bits & MeterType.METER_TYPE_GWZ.value == 0:
        size = 'domestic'
    # Bulk
    else:
        size = 'bulk'
    return size


def set_error_mask(init, channel, arg):
    write_and_verify(init, f'ldacm_data_pulseOutput_errorMask_{channel}', arg.value)


def set_pulse_frequency_in_ticks(init, channel, command, value):
    write_and_verify(init, f'{command}_{channel}', value)


def wait_for_all_pulses(port, pulsebox) -> int:
    # waiting for pulse sending to end
    sleep(5)
    pulses_read = pulsebox.read_pulses(port)
    sleep(30)
    pulses_check = pulsebox.read_pulses(port)
    for x in range(200):
        if pulses_read != pulses_check:
            pulses_read = pulses_check
            sleep(30)
            pulses_check = pulsebox.read_pulses(port)
        else:
            break
    return pulsebox.read_pulses(port)


def set_pulse_config(init, pulse_frequency, valence: int, pulse_output: int, direction: str, pulsebox,
                     set_operation_mode, manual_test: bool = False):
    # go to production mode
    set_operation_mode(OperationMode(mode=MeterMode.PRODUCTION, operation=MeterOperation.NORMAL))

    # fetch map unit
    map_unit = send_command(init, 'Get_ldacm_data_usMeasurementCharacteristicMapUnit',
                            return_parameters=['ldacm_data_usMeasurementCharacteristicMapUnit'])[
        'ldacm_data_usMeasurementCharacteristicMapUnit']

    # configure pulse output for certain valence
    set_pulse_value(init, f'{int(valence / int(MAP_UNIT_VALUE[map_unit]))}', str(pulse_output))

    # configure pulse frequency
    send_command(init, f'Set_ldacm_data_pulseOutput_minHalfPeriode_inTicks_{str(pulse_output)}', pulse_frequency)

    # reset volume accus
    reset_volume_accus(init)

    # set channel output depending on the input parameters
    if direction == "bothWithSign":
        set_pulse_output_channel_type_time(init, '1', direction)
        # set positive burst pulse type
        set_pulse_output_channel_type_time(init, '2', "sign")
        if not manual_test:
            pulsebox.init_pulse_counter('0')
            pulsebox.init_pulse_counter('1')
    else:
        set_pulse_output_channel_type_time(init, str(pulse_output + 1), direction)
        # if there are more channels than 2 as it may be in sharky, close all other channels
        for i in [x for x in range(1, NUM_CHANNELS_SHARKY) if x != pulse_output]:
            set_pulse_output_channel_type_time(init, str(i), "off")
        # init pulse reading
        if not manual_test:
            pulsebox.init_pulse_counter(str(pulse_output))

    # check arduino connection and configuration to be able to detect pulses
    # indices of pulsebox funcs different than commandfile ones, subtract 1
    # set volumeDefinitionsHysteresis_positiv(negative)Border value to zero
    volume_definitions_hysteresis_border(init, 'positiv', '00 00')
    volume_definitions_hysteresis_border(init, 'negativ', '00 00')


@pytest.fixture(scope='function')
def arrange_and_cleanup_pulses(init, get_operation_mode):
    # PRE-CONDITIONS:
    # set operation mode and check if it worked
    returned_mode = get_operation_mode()
    if returned_mode.mode != MeterMode.PRODUCTION and returned_mode.operation != MeterOperation.NORMAL:
        raise Exception('Preconditions not met!')

    yield

    # POST-CONDITIONS:
    returned_mode = get_operation_mode()
    if returned_mode.mode != MeterMode.PRODUCTION and returned_mode.operation != MeterOperation.NORMAL:
        raise Exception('Post-conditions not met! Meter is not in Production Operation')
    # stop simulation if active
    disable_ultrasonic_simulation(init)
    reset_volume_accus(init)
    volume_definitions_hysteresis_border(init, 'positiv', '00 00')
    volume_definitions_hysteresis_border(init, 'negativ', '00 00')
    send_command(init, 'controlMetrologicalLog', '02')
    send_command(init, 'ResetExceptionRecorder')


def pulse_outputs_init(init):
    # turn off pulse output
    if set_pulse_output_channel_type_burst(init, '1', 'off') and set_pulse_output_channel_type_burst(init, '2', 'off'):
        raise Exception('Preconditions not met!')
    sleep(2)


def read_values(init, channel, command):
    value = send_command(init, f'Get_{command}_{channel}',
                         return_parameters=[f'{command}_{channel}'])[f'{command}_{channel}']
    return value


def simulate_flow(ultrasonic_simulation, direction: str = "forward", speed: int = 550):
    phase_shift_int = speed if direction == 'forward' else -speed
    ultrasonic_simulation(simulation_mode=UltrasonicSimulationMode.NORMAL, phase_shift_diff=phase_shift_int * 1024,
                          medium_temperature=270, resonator_calibration=False, time_difference_1us=4000,
                          sonic_speed_correction=19665)


def start_high_res_test(init: ItepMock, direction: str = "forward"):
    po_mode = PulseOutputMode.TIME_CORRECT_INCREMENT_POSITIVE if direction == 'forward' else PulseOutputMode.TIME_CORRECT_INCREMENT_NEGATIVE
    start_high_resolution_test(init, po_mode)


# **********************************
# External Functions
# **********************************

@pytest.mark.pulses
@pytest.mark.test_id('c4850647-27d5-4c60-9389-16c4482716cb')
@pytest.mark.req_ids(['F285', 'F286', 'F287', 'F440', 'F533', 'F439', 'F293', 'F294'])
@pytest.mark.creator('Artur Kulgawczuk')
@pytest.mark.creation_date('15.01.2021')
@allure.title('Pulse output direction, valance and frequency')
@allure.description('The flow sensor shall provide backward and forward direction and accumulate volume increments in '
                    'volume accus.')
@pytest.mark.parametrize('direction', ['positive', 'negative', 'bothWithSign'])
@pytest.mark.parametrize('frequency', ['8', '50', '128, 200'])
@pytest.mark.parametrize('valence', [100, 1000, 2500, 10000, 25000, 100000, 250000])
@pytest.mark.parametrize('flowValue', [451, 542])
@pytest.mark.parametrize('channel', [0, 1])
def test_pulse_output_direction(init, channel, pulsebox, direction, frequency, valence, flowValue, set_operation_mode,
                                ultrasonic_simulation):
    # PRECONDITIONS BLOCK
    # configure pulse output properties and init pulsebox
    set_pulse_config(init, HALFPERIODE_IN_TICK[frequency], valence, channel, direction, pulsebox,
                     set_operation_mode)
    # TEST BLOCK
    # go to production mode
    set_operation_mode(OperationMode(mode=MeterMode.PRODUCTION, operation=MeterOperation.NORMAL))

    # start simulation, wait a bit and stop
    sim_direction = "forward" if direction == "positive" else "negative"
    simulate_flow(ultrasonic_simulation, sim_direction, flowValue)
    sleep(60)
    disable_ultrasonic_simulation(init)
    # wait for the meter to finish sending pulses
    pulses_read = wait_for_all_pulses(str(channel), pulsebox)
    volume_from_pulses = round_pulses_to_resolution(pulsebox.wait_for_all_pulses(str(channel), pulsebox), valence,
                                                    create_multiplier(init))
    volume_from_accu = get_volume_definition(init, direction)

    # POST-CONDITIONS:
    # creating allure report
    allure.attach(f"""
                             <h2>Test result</h2>
                             <table style="width:100%">
                               <tr>
                                 <th>Pulse channel:</th>
                                 <th>[Accu] Measured level/th>
                                 <th>[Pulses] Measured level</th>
                               </tr>
                               <tr align="center">
                                 <td>{channel}</td>
                                 <td>{volume_from_accu}</td>
                                 <td>{volume_from_pulses}</td>
                               </tr>
                             </table>
                             """,
                  'Test result',
                  allure.attachment_type.HTML)

    # Setting meter to default state after test:
    set_operation_mode(OperationMode(mode=MeterMode.PRODUCTION, operation=MeterOperation.NORMAL))
    set_pulse_output_channel_type_time(init, str(channel + 1), 'off')
    # Expected Results:
    assert volume_from_pulses == volume_from_accu


@pytest.mark.pulses
@pytest.mark.test_id('07e61633-e643-4eda-91dc-9a538c52a86d')
@pytest.mark.req_ids(['F401', 'F402', 'F403', 'F404', 'F407', 'F409'])
@pytest.mark.creator('Artur Kulgawczuk')
@pytest.mark.creation_date('15.01.2021')
@allure.title('Pulse outputs in high resolution test')
@allure.description('Test pulse outputs and configurations when the high definition test is active.')
@pytest.mark.parametrize('direction', ['positive', 'negative', 'bothWithSign'])
@pytest.mark.parametrize('frequency', ['8', '50', '128, 200'])
@pytest.mark.parametrize('valence', [100, 1000, 2500, 10000, 25000, 100000, 250000])
@pytest.mark.parametrize('channel', [2])
def test_pulse_outputs_in_high_resolution_test(init, channel,
                                               pulsebox, direction, frequency, valence, set_operation_mode,
                                               ultrasonic_simulation):
    # PRECONDITIONS BLOCK
    # configure pulse output properties and init pulsebox
    # TODO: command for setting Qp not ready, for now continue without setting Qp instead
    set_pulse_config(init, HALFPERIODE_IN_TICK[frequency], valence, channel, direction, pulsebox,
                     set_operation_mode)

    # TEST BLOCK
    # go to production mode
    set_operation_mode(OperationMode(mode=MeterMode.PRODUCTION, operation=MeterOperation.NORMAL))

    # start simulation, wait a bit and stop
    sim_direction = "forward" if direction == "positive" else "negative"
    # set flow value to arbitrary number without parametrisation
    # start flow simulation and run high res test
    simulate_flow(ultrasonic_simulation, sim_direction, 564)
    start_high_res_test(init, direction)
    sleep(60)

    # stop both simulation and high res test
    disable_ultrasonic_simulation(init)
    stop_high_resolution_test(init)

    # wait for the meter to finish sending pulses

    volume_from_pulses = round_pulses_to_resolution(pulsebox.wait_for_all_pulses(str(channel), pulsebox), valence,
                                                    create_multiplier(init))
    volume_from_accu = get_volume_definition(init, direction)

    allure.attach(f"""
                                 <h2>Test result</h2>
                                 <table style="width:100%">
                                   <tr>
                                     <th>Pulse channel:</th>
                                     <th>[Accu] Measured level/th>
                                     <th>[Pulses] Measured level</th>
                                   </tr>
                                   <tr align="center">
                                     <td>{channel}</td>
                                     <td>{volume_from_accu}</td>
                                     <td>{volume_from_pulses}</td>
                                   </tr>
                                 </table>
                                 """,
                  'Test result',
                  allure.attachment_type.HTML)

    # Setting meter to default state after test:
    set_operation_mode(OperationMode(mode=MeterMode.PRODUCTION, operation=MeterOperation.NORMAL))
    set_pulse_output_channel_type_time(init, str(channel + 1), 'off')

    # Expected Results:
    assert volume_from_pulses == volume_from_accu


@pytest.mark.manual_test
@pytest.mark.pulses
@pytest.mark.test_id('4e77d591-ee96-4775-b404-f7194a445148')
@pytest.mark.req_ids(['F443', 'F173', 'F445'])
@pytest.mark.creator('Artur Kulgawczuk')
@pytest.mark.creation_date('15.01.2021')
@allure.title('Pulse output with oscilloscope')
@allure.description('Manual test pulse output with using oscilloscope. Test pulse width, pulse pause etc.')
@pytest.mark.parametrize('direction', ['positive', 'negative', 'bothWithSign'])
@pytest.mark.parametrize('frequency', ['8', '50', '128', '200', '600'])
@pytest.mark.parametrize('channel', [0])
def test_pulse_output_direction(init,
                                pulsebox, direction, frequency, set_operation_mode,
                                ultrasonic_simulation, channel):
    # TEST BLOCK
    # go to production mode
    set_operation_mode(OperationMode(mode=MeterMode.PRODUCTION, operation=MeterOperation.NORMAL))
    # configure pulse output properties
    set_pulse_config(init, HALFPERIODE_IN_TICK[frequency], 1000, channel, direction, pulsebox,
                     set_operation_mode, manual_test=True)

    # start simulation, wait a bit and stop
    sim_direction = "forward" if direction == "positive" else "negative"
    simulate_flow(ultrasonic_simulation, sim_direction, 2115)
    sleep(60)
    disable_ultrasonic_simulation(init)

    # wait for the meter to finish sending pulses
    # IMPORTANT: set a breakpoint here for manual testing
    sleep(1)

    # Setting meter to default state after test:
    set_operation_mode(OperationMode(mode=MeterMode.PRODUCTION, operation=MeterOperation.NORMAL))


@pytest.mark.manual_test
@pytest.mark.pulses
@pytest.mark.test_id('e83590fe-dc48-44d5-bc94-8115b186e40f')
@pytest.mark.req_ids(['F405', 'F406', 'F408'])
@pytest.mark.creator('Artur Kulgawczuk')
@pytest.mark.creation_date('15.01.2021')
@allure.title('Pulse output in high resolution test with oscilloscope')
@allure.description('Manual test length and width pulse when the high definition test is active.')
@pytest.mark.parametrize('direction', ['positive', 'negative', 'bothWithSign'])
@pytest.mark.parametrize('frequency', ['8', '50', '128, 200'])
@pytest.mark.parametrize('valence', [100, 1000, 2500, 10000, 25000, 100000, 250000])
@pytest.mark.parametrize('flowValue', [15195, 894864])
@pytest.mark.parametrize('channel', [0])
def test_pulse_output_direction(init,
                                pulsebox, direction, frequency, valence, flowValue, set_operation_mode,
                                ultrasonic_simulation, channel):
    # TEST BLOCK
    # go to production mode
    set_operation_mode(OperationMode(mode=MeterMode.PRODUCTION, operation=MeterOperation.NORMAL))
    # configure pulse output properties
    set_pulse_config(init, HALFPERIODE_IN_TICK[frequency], 1000, channel, direction, pulsebox,
                     set_operation_mode, manual_test=True)

    # simulate flow for a bit and stop
    sim_direction = "forward" if direction == "positive" else "negative"
    simulate_flow(ultrasonic_simulation, sim_direction, flowValue)
    start_high_res_test(init, direction)
    sleep(60)
    disable_ultrasonic_simulation(init)
    stop_high_resolution_test(init)

    # wait for the meter to finish sending pulses
    # IMPORTANT: set a breakpoint here for manual testing
    sleep(1)

    # Setting meter to default state after test:
    set_operation_mode(OperationMode(mode=MeterMode.PRODUCTION, operation=MeterOperation.NORMAL))


@pytest.mark.pulses
@pytest.mark.test_id('051d7d0c-0137-434c-91c5-ede67c1696a1')
@pytest.mark.req_ids(['F441', 'F442'])
@pytest.mark.creator('Artur Kulgawczuk')
@pytest.mark.creation_date('15.01.2021')
@allure.title('Pulse outputs in high resolution test')
@allure.description('Test pulse output buffer when flow is too high.')
@pytest.mark.parametrize('direction', ['positive', 'negative', 'bothWithSign'])
@pytest.mark.parametrize('channel', [0])
def test_pulse_outputs_buffer(init, channel,
                              pulsebox, direction, set_operation_mode,
                              ultrasonic_simulation):
    # PRECONDITIONS BLOCK
    # configure pulse output properties
    set_pulse_config(init, HALFPERIODE_IN_TICK['50'], 1000, channel, direction, pulsebox,
                     set_operation_mode)
    # TEST BLOCK
    # go to production mode
    set_operation_mode(OperationMode(mode=MeterMode.PRODUCTION, operation=MeterOperation.NORMAL))

    # start simulation with very high flowValue, wait a bit and stop
    sim_direction = "forward" if direction == "positive" else "negative"
    simulate_flow(ultrasonic_simulation, sim_direction, 894864)

    # wait 3 minutes
    sleep(3 * 60)

    # read pulses
    pulses_read_while_buffering = pulsebox.read_pulses(str(channel))

    # stop simulation
    disable_ultrasonic_simulation(init)

    # check pulse output again
    pulses_read_after_buffering = pulsebox.read_pulses(str(channel))

    # wait 7 min
    sleep(7 * 60)

    # check pulse output again
    pulses_final_ctr = round_pulses_to_resolution(pulsebox.wait_for_all_pulses(str(channel), pulsebox), 1000,
                                                  create_multiplier(init))

    allure.attach(f"""
                                 <h2>Test result</h2>
                                 <table style="width:100%">
                                   <tr>
                                     <th>Pulse channel:</th>
                                     <th>[Pulses] Pulses while buffering</th>
                                     <th>[Pulses] Pulses right after buffering</th>
                                     <th>[Pulses] Pulses final counter</th>
                                   </tr>
                                   <tr align="center">
                                     <td>{channel}</td>
                                     <td>{pulses_read_while_buffering}</td>
                                     <td>{pulses_read_after_buffering}</td>
                                     <td>{pulses_final_ctr}</td>
                                   </tr>
                                 </table>
                                 """,
                  'Test result',
                  allure.attachment_type.HTML)

    # Setting meter to default state after test:
    set_operation_mode(OperationMode(mode=MeterMode.PRODUCTION, operation=MeterOperation.NORMAL))
    set_pulse_output_channel_type_time(init, str(channel + 1), 'off')

    # Expected Results:
    assert pulses_read_while_buffering == 0
    assert pulses_read_after_buffering == 0
    assert pulses_final_ctr > 0


@pytest.mark.pulses
@pytest.mark.test_id('2837b64b-2dbc-4d9e-a99f-e615ca229d6d')
@pytest.mark.req_ids(['NoReq'])
@pytest.mark.creator('Artur Kulgawczuk')
@pytest.mark.creation_date('15.01.2021')
@allure.title('Pulse output after reset')
@allure.description(
    'This test checks if pulse configurations and pulse count are kept intact after resetting the meter.')
@pytest.mark.parametrize('channel', [0])
def test_pulse_output_after_reset(init, channel,
                                  pulsebox, set_operation_mode,
                                  ultrasonic_simulation):
    # PRECONDITIONS BLOCK
    # init pulsebox and test just for positive direction
    direction = 'positive'
    set_pulse_config(init, HALFPERIODE_IN_TICK['50'], 1000, channel, direction, pulsebox,
                     set_operation_mode, manual_test=True)
    # TEST BLOCK
    # go to production mode
    set_operation_mode(OperationMode(mode=MeterMode.PRODUCTION, operation=MeterOperation.NORMAL))

    # start simulation, wait a bit and stop
    sim_direction = "forward" if direction == "positive" else "negative"
    simulate_flow(ultrasonic_simulation, sim_direction, 550)

    # simulate some flow for a while
    sleep(60)

    # finish simulation
    disable_ultrasonic_simulation(init)

    #  wait for all pulses and save pulse count
    pulse_ctr_before_reset = pulsebox.wait_for_all_pulses("0", pulsebox)

    # get and save pulse configs
    pulse_info_before_reset = get_pulses_info(init)

    # reset the meter
    send_command(init, 'LowLevelPowerAndReset', parameters='06')

    # check pulse output again, along with pulses config info
    pulse_ctr_after_reset = round_pulses_to_resolution(pulsebox.wait_for_all_pulses(str(channel), pulsebox), 1000,
                                                       create_multiplier(init))
    pulse_info_after_reset = get_pulses_info(init)

    allure.attach(f"""
                                 <h2>Test result</h2>
                                 <table style="width:100%">
                                   <tr>
                                     <th>Pulse channel:</th>
                                     <th>[Pulses] Counter before reset/th>
                                     <th>[Pulses] Counter after reset/th>
                                     <th>[Pulses] Info before reset/th>
                                     <th>[Pulses] Info after reset/th>
                                   </tr>
                                   <tr align="center">
                                     <td>{channel}</td>
                                     <td>{pulse_ctr_before_reset}</td>
                                     <td>{pulse_ctr_after_reset}</td>
                                     <td>{pulse_info_before_reset}</td>
                                     <td>{pulse_info_after_reset}</td>
                                   </tr>
                                 </table>
                                 """,
                  'Test result',
                  allure.attachment_type.HTML)

    # Setting meter to default state after test:
    set_operation_mode(OperationMode(mode=MeterMode.PRODUCTION, operation=MeterOperation.NORMAL))
    set_pulse_output_channel_type_time(init, str(channel + 1), 'off')

    # Expected Results:
    assert pulse_ctr_before_reset == pulse_ctr_after_reset
    assert pulse_info_after_reset == pulse_info_before_reset
