class HexGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def hex_distance(self, pos1, pos2):
        """
        Calculates distance on a hexagonal grid using axial coordinates (q, r).
        We'll treat our given (x, y) coordinates as axial (q, r).
        Distance in axial coords is: (abs(q1-q2) + abs(r1-r2) + abs(q1+r1 - q2-r2)) / 2
        """
        q1, r1 = pos1
        q2, r2 = pos2
        return (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) // 2

    def get_neighbors(self, pos):
        """Returns the 6 immediate neighbors in a hexagonal grid."""
        q, r = pos
        # The 6 directions in axial coordinates
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        neighbors = []
        for dq, dr in directions:
            nq, nr = q + dq, r + dr
            # Optional: constrain to map width/height boundaries here if treating as a literal rectangle
            if self.is_valid_position((nq, nr)):
                neighbors.append((nq, nr))
        return neighbors

    def is_valid_position(self, pos):
        """Basic rectangular bounding box check on axial coords (for simplicity in rendering)."""
        q, r = pos
        return 0 <= q < self.width and 0 <= r < self.height
