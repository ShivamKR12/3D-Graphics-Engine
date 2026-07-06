import pygame as pg
import moderngl as mgl
import sys

# Custom modules
from model import *
from camera import Camera
from light import Light
from mesh import Mesh
from scene import Scene
from scene_renderer import SceneRenderer


class GraphicsEngine:
    """
    The core engine class that initializes and runs the 3D graphics application.
    Handles window creation, OpenGL context setup, main loop, event processing, rendering, and updates.
    """

    def __init__(self, win_size=(1600, 900)):
        """
        Initialize the graphics engine, OpenGL context, and core components like camera, light, mesh, and renderer.

        :param win_size: Tuple specifying the window resolution
        """
        # Initialize Pygame modules
        pg.init()

        # Store window size
        self.WIN_SIZE = win_size

        # Set OpenGL context version to 3.3 Core Profile
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        # Create a window with OpenGL and double buffering
        pg.display.set_mode(self.WIN_SIZE, flags=pg.OPENGL | pg.DOUBLEBUF)

        # Lock mouse to window and hide the cursor for FPS-style camera control
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)

        # Create ModernGL context using the active OpenGL context
        self.ctx = mgl.create_context()
        # Enable depth testing and face culling
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)

        # Clock for managing time
        self.clock = pg.time.Clock()
        self.time = 0           # Current time (seconds)
        self.delta_time = 0     # Time between frames (seconds)

        # Create light source
        self.light = Light()

        # Initialize camera system
        self.camera = Camera(self)

        # Load and manage 3D mesh data
        self.mesh = Mesh(self)

        # Setup the scene
        self.scene = Scene(self)

        # Handles actual rendering of the scene
        self.scene_renderer = SceneRenderer(self)

    def check_events(self):
        """
        Handle user input events. Quit on window close or ESC key press.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                # Cleanup resources before exiting
                self.mesh.destroy()
                self.scene_renderer.destroy()
                pg.quit()
                sys.exit()

    def render(self):
        """
        Clear the frame and render the scene.
        """
        # Clear the color and depth buffers
        self.ctx.clear(color=(0.08, 0.16, 0.18))

        # Delegate rendering to the scene renderer
        self.scene_renderer.render()

        # Swap the front and back buffers (display the rendered frame)
        pg.display.flip()

    def get_time(self):
        """
        Update the current time in seconds.
        """
        self.time = pg.time.get_ticks() * 0.001  # Convert milliseconds to seconds

    def run(self):
        """
        Main application loop. Updates timing, handles input, updates camera, and renders each frame.
        """
        while True:
            self.get_time()         # Update current time
            self.check_events()     # Handle keyboard/window events
            self.camera.update()    # Update camera movement/rotation
            self.render()           # Draw the frame
            self.delta_time = self.clock.tick(60)  # Maintain 60 FPS cap, update delta time


if __name__ == '__main__':
    # Create the application instance and start the main loop
    app = GraphicsEngine()
    app.run()
