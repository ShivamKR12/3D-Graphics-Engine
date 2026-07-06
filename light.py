import glm


class Light:
    """
    A simple directional light class representing a light source in 3D space.
    Includes ambient, diffuse, and specular intensity components, and generates a view matrix from the light's perspective.
    """

    def __init__(self, position=(50, 50, -10), color=(1, 1, 1)):
        """
        Initialize the light source with position, color, and intensity components.

        :param position: Tuple representing the light's position in world space (default is (50, 50, -10))
        :param color: Tuple representing the RGB color/intensity of the light (default is white light (1, 1, 1))
        """
        self.position = glm.vec3(position)  # Light's position in the world
        self.color = glm.vec3(color)        # Light color/intensity
        self.direction = glm.vec3(0, 0, 0)   # Point the light is looking at (origin by default)

        # Lighting components based on Phong lighting model
        self.Ia = 0.06 * self.color  # Ambient intensity (constant low light)
        self.Id = 0.8 * self.color   # Diffuse intensity (directional lighting based on angle)
        self.Is = 1.0 * self.color   # Specular intensity (highlights and reflections)

        # View matrix from the light's point of view (used for shadow mapping, etc.)
        self.m_view_light = self.get_view_matrix()

    def get_view_matrix(self):
        """
        Generates a view matrix from the light's perspective.
        Useful for rendering depth maps in shadow mapping.

        :return: 4x4 view matrix representing the light's "camera" view
        """
        return glm.lookAt(self.position, self.direction, glm.vec3(0, 1, 0))  # Look at origin, with up direction
