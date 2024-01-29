import numpy as np
import matplotlib.pyplot as plt

d = 0.5 # half wavelength spacing
Nr = 2
k = 500
BUF_SIZE = 40000

def calculate_cross_corr(sock2):
    x_correlation_res = b'\x00\x00\x00\x00'
    while (x_correlation_res == b'\x00\x00\x00\x00'):
        x_correlation_res, addr = sock2.recvfrom(4)

    x_correlation_res = int.from_bytes(x_correlation_res, byteorder='little', signed=True)
    return x_correlation_res

def calculate_doa(sock0, sock1, x_correlation_res):
    primary_buf, addr = sock0.recvfrom(BUF_SIZE)
    secondary_buf, addr = sock1.recvfrom(BUF_SIZE)
    primary_cap_signal_whole = np.frombuffer(primary_buf, dtype=np.complex64)
    secondary_cap_signal_whole = np.frombuffer(secondary_buf, dtype=np.complex64)

    if (x_correlation_res > 0):
        primary_cap_signal_whole = np.reshape(primary_cap_signal_whole[x_correlation_res:], (1, primary_cap_signal_whole.shape[0] - x_correlation_res))
        secondary_cap_signal_whole = np.reshape(secondary_cap_signal_whole[:primary_cap_signal_whole.shape[1]], (1, primary_cap_signal_whole.shape[1]))
    else:
        x_correlation_res = abs(x_correlation_res)
        secondary_cap_signal_whole = np.reshape(secondary_cap_signal_whole[x_correlation_res:], (1, secondary_cap_signal_whole.shape[0] - x_correlation_res))
        primary_cap_signal_whole = np.reshape(primary_cap_signal_whole[:secondary_cap_signal_whole.shape[1]], (1, secondary_cap_signal_whole.shape[1]))
    assert(primary_cap_signal_whole.shape == secondary_cap_signal_whole.shape)

    # primary_cap_signal_whole = primary_cap_signal_whole[:-k:k]
    # secondary_cap_signal_whole = secondary_cap_signal_whole[:-k:k]
    assert(primary_cap_signal_whole.shape == secondary_cap_signal_whole.shape)

    cap_signal_whole = np.vstack((primary_cap_signal_whole, secondary_cap_signal_whole))

    theta_scan = np.linspace(-1*np.pi, np.pi, 1000) # 100 different thetas between -180 and +180 degrees
    results = []

    # Eigenvector method - we have the array factor, so apply it to each row of the signal matrix
    for theta_i in theta_scan:
        # For a particular theta, calculate the array factor
        w = np.asmatrix(np.exp(-2j * np.pi * d * np.arange(Nr) * np.sin(theta_i)))
        # Multiply it against the received signal (row 0 is primary signal capture, row 1 is secondary signal capture)
        r_weighted = np.conj(w) @ cap_signal_whole
        # Converting to real numbers since the capture comes in complex form (IIRC)
        r_weighted = np.asarray(r_weighted).squeeze()
        results.append(np.mean(np.abs(r_weighted)**2))

    # Add the angle that
    return(theta_scan[np.argmax(results)] * 180 / np.pi)