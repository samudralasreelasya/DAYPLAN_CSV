"""Shared geo math used by any service that needs distance calculations."""
import math

import numpy as np

# Kilometres covered by one degree of latitude on a sphere of radius 6371 km.
KM_PER_DEGREE = math.pi * 6371 / 180


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km between two lat/lon points."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def _haversine_km_vec(lat1, lon1, lat2, lon2):
    """Same formula as haversine_km, but for whole numpy arrays at once."""
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = phi2 - phi1
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    return 6371 * 2 * np.arcsin(np.sqrt(a))


class RouteIndex:
    """A route line prepared for fast "how close is this place?" questions.

    A route (from OSRM) is a long list of points. Between two neighbouring
    points the road is treated as a straight piece called a SEGMENT. For any
    place we measure the gap to the nearest point ON a segment - not just to
    the route's own points, which can be tens of km apart on a highway.

    Build it ONCE per route, then call locate() for many places.
    """

    def __init__(self, coordinates):
        """coordinates: GeoJSON style [[lon, lat], ...], exactly what OSRM returns."""
        pts = np.asarray(coordinates, dtype=float)
        if pts.ndim != 2 or pts.shape[0] < 2 or pts.shape[1] < 2:
            raise ValueError("A route needs at least two [lon, lat] points")

        self.lons = pts[:, 0]
        self.lats = pts[:, 1]

        # Length of every segment, and how far from the route's start each segment begins.
        self.segment_km = _haversine_km_vec(
            self.lats[:-1], self.lons[:-1], self.lats[1:], self.lons[1:]
        )
        self.start_km = np.concatenate(([0.0], np.cumsum(self.segment_km)[:-1]))
        self.total_km = float(self.segment_km.sum())

    def locate(self, lat, lon):
        """Return (off_route_km, along_route_km) for a place.

        off_route_km   - straight-line gap between the place and the road
        along_route_km - how far from the START of the route that closest point is
        """
        # Work on a small flat map centred on the place. At the few-km scale
        # that matters for a corridor, the error from ignoring the Earth's
        # curvature is tiny. Longitude degrees shrink with latitude (cos).
        cos_lat = math.cos(math.radians(lat))
        ax = (self.lons[:-1] - lon) * cos_lat * KM_PER_DEGREE
        ay = (self.lats[:-1] - lat) * KM_PER_DEGREE
        bx = (self.lons[1:] - lon) * cos_lat * KM_PER_DEGREE
        by = (self.lats[1:] - lat) * KM_PER_DEGREE

        # For each segment A->B, find the point on it closest to the place
        # (which sits at the origin). t is how far along the segment that point
        # is: 0 = at A, 1 = at B. Clipping keeps it ON the segment.
        dx, dy = bx - ax, by - ay
        seg_len_sq = dx * dx + dy * dy
        with np.errstate(divide="ignore", invalid="ignore"):
            t = np.where(seg_len_sq > 0, -(ax * dx + ay * dy) / seg_len_sq, 0.0)
        t = np.clip(t, 0.0, 1.0)

        gap = np.hypot(ax + t * dx, ay + t * dy)
        best = int(np.argmin(gap))
        along = self.start_km[best] + t[best] * self.segment_km[best]
        return float(gap[best]), float(along)