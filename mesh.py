from vao import VAO
from texture import Texture


class Mesh:
    """
    Represents a 3D mesh object composed of a VAO (vertex array object) and a texture.
    Responsible for managing GPU resources related to geometry and texture data.
    """

    def __init__(self, app):
        """
        Initialize the mesh by creating a VAO and loading a texture.

        :param app: Reference to the main application, which provides the rendering context.
        """
        self.app = app  # Store reference to the app for access to context and shared data

        # Create Vertex Array Object to store geometry buffers (vertices, indices, etc.)
        self.vao = VAO(app.ctx)

        # Load and bind texture for the mesh
        self.texture = Texture(app)

    def destroy(self):
        """
        Clean up GPU resources associated with the mesh.
        """
        self.vao.destroy()     # Free VAO and associated buffers
        self.texture.destroy() # Free texture resource
