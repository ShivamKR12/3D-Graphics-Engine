from model import *
import glm


class Scene:
    """
    Represents the 3D scene graph containing objects to be rendered.

    Responsibilities:
    - Loading and positioning all scene objects
    - Managing the skybox
    - Updating dynamic elements (e.g., animations)
    """

    def __init__(self, app):
        """
        Initialize the scene and load all static and dynamic content.

        Args:
            app: The main application instance providing context and resources.
        """
        self.app = app
        self.objects = []  # List to hold all 3D objects in the scene
        self.load()  # Load and populate the scene

        # Create and assign the advanced skybox
        self.skybox = AdvancedSkyBox(app)

    def add_object(self, obj):
        """
        Add a model object to the scene.

        Args:
            obj: An instance of a model (e.g., Cube, Cat, etc.)
        """
        self.objects.append(obj)

    def load(self):
        """
        Populate the scene with default objects: floor, columns, a cat model,
        and a moving cube for animation testing.
        """
        app = self.app
        add = self.add_object

        # Create a tiled floor using cubes
        n, s = 20, 2  # 'n' is the range limit, 's' is the spacing
        for x in range(-n, n, s):
            for z in range(-n, n, s):
                add(Cube(app, pos=(x, -s, z)))  # Position cubes at ground level

        # Add two diagonal column structures using textured cubes (tex_id=2)
        for i in range(9):
            add(Cube(app, pos=(15, i * s, -9 + i), tex_id=2))  # Left diagonal column
            add(Cube(app, pos=(15, i * s, 5 - i), tex_id=2))   # Right diagonal column

        # Add a static cat model
        add(Cat(app, pos=(0, -1, -10)))

        # Create and add a moving cube with a different texture and larger scale
        self.moving_cube = MovingCube(app, pos=(0, 6, 8), scale=(3, 3, 3), tex_id=1)
        add(self.moving_cube)

    def update(self):
        """
        Update scene logic every frame.

        For now, rotates the moving cube based on elapsed app time.
        """
        self.moving_cube.rot.xyz = self.app.time  # Rotate cube in all axes using app time
