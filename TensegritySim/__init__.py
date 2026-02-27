"""
TensegritySim Package

This package provides tools for simulating and visualizing tensegrity structures.
"""

from .data_structures import Node, Connection, Surface, Tensegrity, NonlinProps, ConnectionNonlinear
from .yaml_parser import YamlParser
from .visualization import Visualization
from .tensegrity_solver import TensegritySolver

__all__ = ["Node", "Connection", "Surface", "Tensegrity",
           "NonlinProps", "ConnectionNonlinear",
           "YamlParser", "Visualization", "TensegritySolver"]

version = "1.0.1"
