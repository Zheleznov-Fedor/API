def scale(top):
    top_coord = top["Point"]["pos"]
    top_longitude, top_lattitude = top_coord.split(" ")
    return top_longitude, top_lattitude