# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.node import Node
import socket
from std_msgs.msg import String
import gr_pubsub.custom_doa.custom_doa as custom_doa

UDP_IP = "127.0.0.1"
PRIMARY_UDP_PORT = 5000
SECONDARY_UDP_PORT = 5001
CROSS_CORRELATION_PORT = 5003

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.001  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.sock0 = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
        self.sock0.bind((UDP_IP, PRIMARY_UDP_PORT))
        self.sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock1.bind((UDP_IP, SECONDARY_UDP_PORT))
        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock2.bind((UDP_IP, CROSS_CORRELATION_PORT))
        self.x_correlation_res = custom_doa.calculate_cross_corr(self.sock2)

    def timer_callback(self):
        doa = custom_doa.calculate_doa(self.sock0, self.sock1, self.x_correlation_res)
        msg = String()
        msg.data = str(doa)
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
