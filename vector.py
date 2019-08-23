from pyglet import graphics, gl, text
from random import random
from math import floor
from copy import deepcopy

class Plane(object):
    def __init__(self, window, basis=[1.0, 1.0], gridlines=8):
        # The vectors that belong to this plane
        self.vectors = list()
        # The plane basis vectors
        self.basis = basis
        # The size of the window this plane will be rendered to
        self.window_size = [window.width, window.height]
        # The number of gridline subdivisions
        self.gridlines = gridlines

    def _transform_to_plane_coordinates(self, window_coordinates):
        ''' Transforms window coordinates to plane coordinates '''
        w, h = self.window_size[0], self.window_size[1]
        
        new_coordinates = deepcopy(window_coordinates)
        if type(new_coordinates) is tuple:
            new_coordinates = [new_coordinates[0], new_coordinates[1]]
        # ((0, w), (0, h)) --> ((0, 1), (0, 1))
        new_coordinates[0] /= w
        new_coordinates[1] /= h
 
        # --> ((-0.5, 0.5), (-0.5, 0.5))
        new_coordinates[0] -= 0.5
        new_coordinates[1] -= 0.5

        # --> ((-1, 1), (-1, 1))
        new_coordinates[0] *= 2
        new_coordinates[1] *= 2

        # --> ((-i, i), (-j, j))
        new_coordinates[0] *= self.basis[0]
        new_coordinates[1] *= self.basis[1]
        return (new_coordinates[0], new_coordinates[1])

    def _transform_to_window_coordinates(self, plane_coordinates):
        ''' Transforms plane coordinates to window coordinates '''
        new_coordinates = deepcopy(plane_coordinates)
        w, h = self.window_size[0], self.window_size[1]
        if type(new_coordinates) is tuple:
            new_coordinates = [new_coordinates[0], new_coordinates[1]]

        # ((-i, i), (-j, j)) --> ((0, 2i), (0, 2j))
        new_coordinates[0] += self.basis[0]
        new_coordinates[1] += self.basis[1]

        # --> ((0, 2i*w), (0, 2j*h))
        new_coordinates[0] *= w
        new_coordinates[1] *= h

        # --> ((0, w), (0, h))
        new_coordinates[0] /= (2 * self.basis[0])
        new_coordinates[1] /= (2 * self.basis[1])
        return (new_coordinates[0], new_coordinates[1])

    def append_windowspace(self, vector):
        ''' Appends a vector with windowspace coordinates to self.vector
            after transforming to planespace coordinates '''
        # Transform window-space coordinates to plane-space coordinates
        planespace_vector_origin = self._transform_to_plane_coordinates(
            vector.origin
        )
        planespace_vector_endpoint = self._transform_to_plane_coordinates(
            vector.endpoint
        )
        planespace_vector = Vector(
            planespace_vector_origin,
            planespace_vector_endpoint,
            vector.color
        )
        # Append transformed vector to list
        self.vectors.append(planespace_vector)

    def append_planespace(self, vector):
        ''' Appends a vector with planespace coordinates to self.vector '''
        self.vectors.append(vector)

    def batch(self, batch=None, show_basis_vectors=True, show_endpoint_coordinates=True):
        ''' Returns a pyglet.graphics.Batch containing vertex lists for
            all vectors in self.vectors, the basis vectors, and gridlines. '''
        if batch is None:
            batch = graphics.Batch()

        if self.gridlines > 1:
            i_hat = self.basis[0]
            j_hat = self.basis[1]
            for i in range(0, self.gridlines):
                j_hat = self.basis[1]
                y = -j_hat + i * (2/self.gridlines)
                v0 = self._transform_to_window_coordinates([-j_hat, y])
                v1 = self._transform_to_window_coordinates([j_hat, y])
                batch.add(2, gl.GL_LINES, None,
                    ('v2f', [v0[0], v0[1], v1[0], v1[1]]),
                    ('c4B', [64, 64, 64, 1]*2)
                )

            for j in range(0, self.gridlines):
                x = -i_hat + j * (2/self.gridlines)
                v0 = self._transform_to_window_coordinates([x, -i_hat])
                v1 = self._transform_to_window_coordinates([x, i_hat])
                batch.add(2, gl.GL_LINES, None,
                    ('v2f', [v0[0], v0[1], v1[0], v1[1]]),
                    ('c4B', [64, 64, 64, 1]*2)
                )

        if show_basis_vectors is True:
            # Add basis vector lines to batch
            # i^
            v0 = self._transform_to_window_coordinates([0, 0])
            v1 = self._transform_to_window_coordinates([self.basis[0], 0])
            color = [1.0, 0.0, 0.0]
            batch.add(2, gl.GL_LINES, None,
                ('v2f', [v0[0], v0[1], v1[0], v1[1]]),
                ('c3f', color*2)
            )

            # j^
            v0 = self._transform_to_window_coordinates([0, 0])
            v1 = self._transform_to_window_coordinates([0, self.basis[1]])
            color = [0.0, 1.0, 0.0]
            batch.add(2, gl.GL_LINES, None,
                ('v2f', [v0[0], v0[1], v1[0], v1[1]]),
                ('c3f', color*2)
            )

        for vector in self.vectors:
            # Add vector lines to batch
            v0 = self._transform_to_window_coordinates(vector.origin)
            v1 = self._transform_to_window_coordinates(vector.endpoint)
            batch.add(2, gl.GL_LINES, None,
                ('v2f', [v0[0], v0[1], v1[0], v1[1]]),
                ('c3f', vector.color*2)
            )
            if show_endpoint_coordinates is True:
                # Display planespace coordinates
                x = round(vector.endpoint[0], 3)
                y = round(vector.endpoint[1], 3)
                text.Label(str(x) + ", " + str(y),
                            font_name='Consolas',
                            font_size=12,
                            x=v1[0]+10, y=v1[1]+10).draw()


        return batch

class Vector(object):
    ''' An algebraic vector in 2R '''
    def __init__(self, origin=[0.0, 0.0], endpoint=[1.0, 1.0], color=0):
        self.origin = origin
        self.endpoint = endpoint
        if color == 0:
            self.color = [random(), random(), random()]
        else:
            self.color = color

    def draw(self, window):
        w, h = window.width/2, window.height/2
        graphics.draw(2, gl.GL_LINES, 
        ('v2f', [(self.origin[0]+w),
                 (self.origin[1]+h),
                 (self.endpoint[0]+w), 
                 (self.endpoint[1]+h)]),
        ('c3f', self.color*2))

    def __add__(self, other):
        if type(other) is Vector:
            new_vector_endpoint = [self.endpoint[0] + other.endpoint[0],
                                   self.endpoint[1] + other.endpoint[1]]
            new_vector = Vector(self.origin, new_vector_endpoint)
            return new_vector
        if type(other) is list:
            new_vector_endpoint = [self.endpoint[0] + other[0],
                                   self.endpoint[1] + other[1]]
            new_vector = Vector(self.origin, new_vector_endpoint)
            return new_vector

    def __sub__(self, other):
        if type(other) is Vector:
            new_vector_endpoint = [self.endpoint[0] - other.endpoint[0],
                                   self.endpoint[1] - other.endpoint[1]]
            new_vector = Vector(self.origin, new_vector_endpoint)
            return new_vector
        if type(other) is list:
            new_vector_endpoint = [self.endpoint[0] - other[0],
                                   self.endpoint[1] - other[1]]
            new_vector = Vector(self.origin, new_vector_endpoint)
            return new_vector

    def __mul__(self, other):
        if type(other) is Vector:
            new_vector_endpoint = [self.endpoint[0] * other.endpoint[0],
                                   self.endpoint[1] * other.endpoint[1]]
            new_vector = Vector(self.origin, new_vector_endpoint)
            return new_vector
        if type(other) is list:
            new_vector_endpoint = [self.endpoint[0] * other[0],
                                   self.endpoint[1] * other[1]]
            new_vector = Vector(self.origin, new_vector_endpoint)
            return new_vector
        
    def __rmul__(self, other):
        return self.__mul__(other)

    def dot(self, other):
        if type(other) is Vector:
            return self.endpoint[0] * other.endpoint[0] + self.endpoint[1] * other.endpoint[1]
        if type(other) is list:
            return self.endpoint[0] * other[0] + self.endpoint[1] * other[1]

    def __iadd__(self, other):
        self.endpoint[0] += other.endpoint[0]
        self.endpoint[1] += other.endpoint[1]

    def __isub__(self, other):
        self.endpoint[0] -= other.endpoint[0]
        self.endpoint[1] -= other.endpoint[1]

    def __imul__(self, other):
        self.endpoint[0] *= other.endpoint[0]
        self.endpoint[1] *= other.endpoint[1]