# gr_pubsub

Takes three data streams from a GNURadio direction of arrival runtime and uses the eigenvector method to calculate the angle of arrival.

Pushes resulting value to ROS2 pub/sub topic (for later use with wheeled robot controls).