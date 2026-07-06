import glm
import pygame as pg

# Camera settings
FOV = 50  # Field of view in degrees
NEAR = 0.1  # Near clipping plane
FAR = 100  # Far clipping plane
SPEED = 0.005  # Camera movement speed
SENSITIVITY = 0.04  # Mouse sensitivity for looking around


class Camera:
    """
    A 3D camera class for handling movement, rotation, and view/projection matrix calculation.
    Uses OpenGL Mathematics (GLM) for vector and matrix operations.
    """

    def __init__(self, app, position=(0, 0, 4), yaw=-90, pitch=0):
        """
        Initialize the camera with default or provided position, yaw, and pitch.

        :param app: Reference to the main application (used for window size and delta time)
        :param position: Initial position of the camera in 3D space
        :param yaw: Horizontal rotation in degrees
        :param pitch: Vertical rotation in degrees
        """
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]
        self.position = glm.vec3(position)
        self.up = glm.vec3(0, 1, 0)  # World up vector
        self.right = glm.vec3(1, 0, 0)  # Local right vector
        self.forward = glm.vec3(0, 0, -1)  # Looking forward
        self.yaw = yaw
        self.pitch = pitch

        # Initialize view and projection matrices
        self.m_view = self.get_view_matrix()
        self.m_proj = self.get_projection_matrix()

    def rotate(self):
        """
        Update yaw and pitch based on mouse movement.
        Mouse movement is captured using pygame's get_rel method.
        """
        rel_x, rel_y = pg.mouse.get_rel()
        self.yaw += rel_x * SENSITIVITY
        self.pitch -= rel_y * SENSITIVITY

        # Clamp pitch to prevent gimbal lock
        self.pitch = max(-89, min(89, self.pitch))

    def update_camera_vectors(self):
        """
        Recalculate forward, right, and up vectors from updated yaw and pitch.
        Ensures that camera orientation reflects mouse movement.
        """
        yaw_rad, pitch_rad = glm.radians(self.yaw), glm.radians(self.pitch)

        # Calculate forward vector
        self.forward.x = glm.cos(yaw_rad) * glm.cos(pitch_rad)
        self.forward.y = glm.sin(pitch_rad)
        self.forward.z = glm.sin(yaw_rad) * glm.cos(pitch_rad)
        self.forward = glm.normalize(self.forward)

        # Calculate right and up vectors from the new forward
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def update(self):
        """
        Update the camera's position, rotation, orientation vectors, and view matrix each frame.
        """
        self.move()
        self.rotate()
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

    def move(self):
        """
        Move the camera based on WASD and QE key inputs.
        Movement is scaled by frame delta time for smooth motion.
        """
        velocity = SPEED * self.app.delta_time
        keys = pg.key.get_pressed()

        if keys[pg.K_w]:  # Move forward
            self.position += self.forward * velocity
        if keys[pg.K_s]:  # Move backward
            self.position -= self.forward * velocity
        if keys[pg.K_a]:  # Strafe left
            self.position -= self.right * velocity
        if keys[pg.K_d]:  # Strafe right
            self.position += self.right * velocity
        if keys[pg.K_q]:  # Move up
            self.position += self.up * velocity
        if keys[pg.K_e]:  # Move down
            self.position -= self.up * velocity

    def get_view_matrix(self):
        """
        Create and return the view matrix using GLM's lookAt function.
        The camera looks from its position toward the forward direction.

        :return: 4x4 view matrix
        """
        return glm.lookAt(self.position, self.position + self.forward, self.up)

    def get_projection_matrix(self):
        """
        Create and return the perspective projection matrix.

        :return: 4x4 projection matrix
        """
        return glm.perspective(glm.radians(FOV), self.aspect_ratio, NEAR, FAR)
