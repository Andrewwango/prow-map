def in_box(lat, long, bbox):
    return (bbox[0] < long) & (long < bbox[2]) & (bbox[1] < lat) & (lat < bbox[3])

def metres_to_dist(m):
    return m / (100 * 1000)