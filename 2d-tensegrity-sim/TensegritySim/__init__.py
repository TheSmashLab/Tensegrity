"""
TensegritySim Package

This package provides tools for simulating and visualizing tensegrity structures.
"""

from .data_structures import Node, Connection, Surface, Tensegrity
from .errors import TensegrityError, TensegrityInputError, TensegrityParseError, TensegritySolveError
from .yaml_parser import YamlParser
from .visualization import Visualization
from .tensegrity_solver import SolverResult, TensegritySolver

__all__ = [
    "Node",
    "Connection",
    "Surface",
    "Tensegrity",
    "TensegrityError",
    "TensegrityInputError",
    "TensegrityParseError",
    "TensegritySolveError",
    "SolverResult",
    "YamlParser",
    "Visualization",
    "TensegritySolver",
]

version = "1.0.0"
