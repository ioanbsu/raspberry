#!/usr/bin/python
import web
import smbus
import math

urls = (
'/', 'index'
)

# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect command


def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)


class index:
    def GET(self):
        accel_xout = read_word_2c(0x3b)
        accel_yout = read_word_2c(0x3d)
        accel_zout = read_word_2c(0x3f)

        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0

        return str(get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))+" "+str(get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))


if __name__ == "__main__":

    # Now wake the 6050 up as it starts in sleep mode
    bus.write_byte_data(address, power_mgmt_1, 0)

    app = web.application(urls, globals())
    app.run()






#
#
# #!/usr/bin/python
# import web
# import smbus
# import math
# import time
#
#
# urls = (
#     '/', 'index'
# )
#
# gyro_scale = 131.0
# accel_scale = 16384.0
#
# # Power management registers
# power_mgmt_1 = 0x6b
# power_mgmt_2 = 0x6c
#
# bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
# address = 0x68       # This is the address value read via the i2cdetect command
#
#
# def read_all():
#     raw_gyro_data = bus.read_i2c_block_data(address, 0x43, 6)
#     raw_accel_data = bus.read_i2c_block_data(address, 0x3b, 6)
#
#     gyro_scaled_x = twos_compliment((raw_gyro_data[0] << 8) + raw_gyro_data[1]) / gyro_scale
#     gyro_scaled_y = twos_compliment((raw_gyro_data[2] << 8) + raw_gyro_data[3]) / gyro_scale
#     gyro_scaled_z = twos_compliment((raw_gyro_data[4] << 8) + raw_gyro_data[5]) / gyro_scale
#
#     accel_scaled_x = twos_compliment((raw_accel_data[0] << 8) + raw_accel_data[1]) / accel_scale
#     accel_scaled_y = twos_compliment((raw_accel_data[2] << 8) + raw_accel_data[3]) / accel_scale
#     accel_scaled_z = twos_compliment((raw_accel_data[4] << 8) + raw_accel_data[5]) / accel_scale
#
#     return (gyro_scaled_x, gyro_scaled_y, gyro_scaled_z, accel_scaled_x, accel_scaled_y, accel_scaled_z)
#
# def twos_compliment(val):
#     if (val >= 0x8000):
#         return -((65535 - val) + 1)
#     else:
#         return val
#
# def dist(a, b):
#     return math.sqrt((a * a) + (b * b))
#
#
# def get_y_rotation(x,y,z):
#     radians = math.atan2(x, dist(y,z))
#     return -math.degrees(radians)
#
# def get_x_rotation(x,y,z):
#     radians = math.atan2(y, dist(x,z))
#     return math.degrees(radians)
#
# def read_word(adr):
#     high = bus.read_byte_data(address, adr)
#     low = bus.read_byte_data(address, adr+1)
#     val = (high << 8) + low
#     return val
#
#
# def read_word_2c(adr):
#     val = read_word(adr)
#     if (val >= 0x8000):
#         return -((65535 - val) + 1)
#     else:
#         return val
#
#
# bus = smbus.SMBus(1)  # or bus = smbus.SMBus(1) for Revision 2 boards
#
# # Now wake the 6050 up as it starts in sleep mode
# bus.write_byte_data(address, power_mgmt_1, 0)
#
# now = time.time()
#
# K = 0.98
# K1 = 1 - K
#
# time_diff = 0.01
#
#
#
# class index:
#     def GET(self):
#         (gyro_scaled_x, gyro_scaled_y, gyro_scaled_z, accel_scaled_x, accel_scaled_y, accel_scaled_z) = read_all()
#
#         last_x = get_x_rotation(accel_scaled_x, accel_scaled_y, accel_scaled_z)
#         last_y = get_y_rotation(accel_scaled_x, accel_scaled_y, accel_scaled_z)
#
#         gyro_offset_x = gyro_scaled_x
#         gyro_offset_y = gyro_scaled_y
#
#         gyro_total_x = (last_x) - gyro_offset_x
#         gyro_total_y = (last_y) - gyro_offset_y
#
#         print "{0:.4f} {1:.2f} {2:.2f} {3:.2f} {4:.2f} {5:.2f} {6:.2f}".format( time.time() - now, (last_x), gyro_total_x, (last_x), (last_y), gyro_total_y, (last_y))
#
#         for i in range(0, int(1.0 / time_diff)):
#             time.sleep(time_diff - 0.005)
#
#             (gyro_scaled_x, gyro_scaled_y, gyro_scaled_z, accel_scaled_x, accel_scaled_y, accel_scaled_z) = read_all()
#
#             gyro_scaled_x -= gyro_offset_x
#             gyro_scaled_y -= gyro_offset_y
#
#             gyro_x_delta = (gyro_scaled_x * time_diff)
#             gyro_y_delta = (gyro_scaled_y * time_diff)
#
#             gyro_total_x += gyro_x_delta
#             gyro_total_y += gyro_y_delta
#
#             rotation_x = get_x_rotation(accel_scaled_x, accel_scaled_y, accel_scaled_z)
#             rotation_y = get_y_rotation(accel_scaled_x, accel_scaled_y, accel_scaled_z)
#
#             last_x = K * (last_x + gyro_x_delta) + (K1 * rotation_x)
#             last_y = K * (last_y + gyro_y_delta) + (K1 * rotation_y)
#
#         return str(rotation_x)+" "+str(rotation_y)
#
#
# if __name__ == "__main__":
#
#     # Now wake the 6050 up as it starts in sleep mode
#     bus.write_byte_data(address, power_mgmt_1, 0)
#
#     app = web.application(urls, globals())
#     app.run()
