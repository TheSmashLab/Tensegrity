import numpy as np
from dataclasses import dataclass
from typing import Dict
from scipy.optimize import least_squares, root
from scipy.sparse import coo_matrix, lil_matrix, vstack

from .data_structures import Connection, Tensegrity


@dataclass
class SolverResult:
    success: bool
    message: str
    scipy_result: object = None


class TensegritySolver:
    """
    TensegritySolver class for solving the positions of nodes in a tensegrity structure.
    This class provides methods to initialize the solver, set forces on nodes, and solve the positions of nodes
    using optimization techniques. It also includes internal functions to compute the objective function, 
    spring connection energy, and its derivatives.
    
    Attributes:
        tensegrity (Tensegrity): The tensegrity object containing nodes and connections.
        dim (int): The dimension of the optimization problem (default is 2).
    """
    def __init__(self, tensegrity: Tensegrity, dim: int = 2) -> None:
        """
        Initializes an Optimization object.

        Args:
            tensegrity (Tensegrity): The tensegrity object containing nodes and connections.
            dim (int): The dimension of the optimization problem (default is 3).

        Raises:
            ValueError: If connection stiffness is less than 0.
        """
        self.tensegrity = tensegrity

        self.dim = dim

        self.node_indices = {node.name: i for i, node in enumerate(self.tensegrity.nodes)}

        self.forces = np.zeros(self.dim*len(self.tensegrity.nodes))
        self._initialize_topology()

    def _initialize_topology(self) -> None:
        """Cache fixed topology and coordinate mappings used by every residual call."""
        self._coordinate_count = self.dim * len(self.tensegrity.nodes)
        self._pinned_values = np.array(
            [node.position[:self.dim] for node in self.tensegrity.nodes],
            dtype=float,
        ).reshape(-1)
        self._free_mask = np.ones(self._coordinate_count, dtype=bool)
        for node, pinned_dimensions in self.tensegrity.pins.items():
            node_index = self.node_indices[node]
            for dimension in range(self.dim):
                if pinned_dimensions[dimension]:
                    self._free_mask[node_index * self.dim + dimension] = False
        self._free_indices = np.flatnonzero(self._free_mask)
        self._free_column = {
            coordinate: column for column, coordinate in enumerate(self._free_indices)
        }

        linked_nodes = self.tensegrity.surface.linked_nodes if self.tensegrity.surface else []
        self._linked_edges = {frozenset(pair) for pair in linked_nodes}
        self._surface_pairs = [
            (self.node_indices[node1], self.node_indices[node2])
            for node1, node2 in linked_nodes
        ]
        self._has_cylinder_constraints = bool(
            self.tensegrity.surface
            and self.tensegrity.surface.shape["surface_type"] == "cylinder"
        )

        self._connection_indices = []
        self._connection_seam_segments = []
        for connection in self.tensegrity.connections:
            indices = np.fromiter(
                (self.node_indices[node.name] for node in connection.nodes),
                dtype=np.intp,
            )
            self._connection_indices.append(indices)
            self._connection_seam_segments.append(
                np.array(
                    [
                        frozenset((connection.nodes[i].name, connection.nodes[i + 1].name))
                        in self._linked_edges
                        for i in range(len(connection.nodes) - 1)
                    ],
                    dtype=bool,
                )
            )
        self._segment_starts = np.concatenate(
            [indices[:-1] for indices in self._connection_indices]
        ) if self._connection_indices else np.array([], dtype=np.intp)
        self._segment_ends = np.concatenate(
            [indices[1:] for indices in self._connection_indices]
        ) if self._connection_indices else np.array([], dtype=np.intp)
        self._segment_connections = np.concatenate(
            [
                np.full(len(indices) - 1, connection_index, dtype=np.intp)
                for connection_index, indices in enumerate(self._connection_indices)
            ]
        ) if self._connection_indices else np.array([], dtype=np.intp)
        self._seam_segment_mask = np.concatenate(
            self._connection_seam_segments
        ) if self._connection_seam_segments else np.array([], dtype=bool)
        self._connection_stiffness = np.array(
            [connection.stiffness for connection in self.tensegrity.connections],
            dtype=float,
        )
        self._connection_initial_lengths = np.array(
            [connection.initial_length for connection in self.tensegrity.connections],
            dtype=float,
        )
        self._string_connections = np.array(
            [
                connection.connection_type == Connection.ConnectionType.STRING
                for connection in self.tensegrity.connections
            ],
            dtype=bool,
        )
        self._two_node_connection_ids = np.array(
            [
                index
                for index, indices in enumerate(self._connection_indices)
                if len(indices) == 2
            ],
            dtype=np.intp,
        )
        self._polyline_connection_ids = np.array(
            [
                index
                for index, indices in enumerate(self._connection_indices)
                if len(indices) != 2
            ],
            dtype=np.intp,
        )

        self._residual_keep_indices, self._surface_merges = self._build_residual_mapping()

    def _build_residual_mapping(self):
        delete_indices = set(np.flatnonzero(~self._free_mask))
        merges = []
        for node1, node2 in self._surface_pairs:
            for dimension in range(min(2, self.dim)):
                index1 = node1 * self.dim + dimension
                index2 = node2 * self.dim + dimension
                if index1 in delete_indices:
                    delete_indices.add(index2)
                elif index2 in delete_indices:
                    delete_indices.add(index1)
                else:
                    merges.append((index1, index2))
                    delete_indices.add(index2)
        keep = np.array(
            [i for i in range(self._coordinate_count) if i not in delete_indices],
            dtype=np.intp,
        )
        return keep, merges

    def set_forces(self, forces: Dict[str, np.ndarray]) -> None:
        """
        Sets the forces on the nodes in the tensegrity structure.
        
        Args:
            forces (Dict[str, np.ndarray]): A dictionary containing the forces on each node.
        
        Raises:
            ValueError: If the force vector does not have the same dimension as the optimization problem.
        """
        self.forces = np.zeros(self.dim*len(self.tensegrity.nodes))

        for node, force in forces.items():
            if len(force) != self.dim:
                raise ValueError("Force vector must have the same dimension as the optimization problem.")

            index = self.node_indices[node]
            self.forces[index*self.dim : index*self.dim + self.dim] = force

    def solve(
        self,
        method: str = "least_squares",
        attempts: int = 8,
        perturbation: float = 0.05,
        residual_tol: float = 1e-6,
        force_tol: float = 1e-8,
        max_zero_force_fraction: float = 0.5,
        random_seed: int = 0,
    ) -> SolverResult:
        """
        Solves the position of nodes in the tensegrity structure.
        
        This method solves for zero virtual work. By default it uses a least-squares
        residual solve with several initial guesses, then rejects numerical successes
        that leave a prestressed structure with most members carrying zero force.
        
        Args:
            method (str): "least_squares" for the robust default path, or a scipy.optimize.root method.
            attempts (int): Number of initial guesses to try for the least-squares path.
            perturbation (float): Relative random perturbation size for retry guesses.
            residual_tol (float): Maximum acceptable objective residual norm.
            force_tol (float): Force magnitude treated as zero when checking null solutions.
            max_zero_force_fraction (float): Reject prestressed solutions with at least this fraction
                of zero-force connections.
            random_seed (int): Seed for deterministic retry perturbations.
        
        Returns:
            SolverResult. On success, changes are made internally to the Tensegrity object.
        """
        # Controls can change member rest lengths between interactive solves.
        # Refresh mutable mechanical properties before evaluating the next state.
        self._refresh_connection_parameters()
        if method != "least_squares":
            return self._solve_with_root(method, force_tol, max_zero_force_fraction)

        x0 = self._create_initial_guess() # The current positions of the nodes (excluding pinned nodes)
        if len(x0) == 0:
            self.tensegrity.update_forces()
            return SolverResult(True, "No free coordinates to solve.", None)

        guesses = self._create_initial_guesses(x0, attempts, perturbation, random_seed)
        best_result = None
        best_residual_norm = np.inf
        residual_count = len(self._objective(x0))
        use_dense_lm = residual_count >= len(x0) and len(x0) <= 500
        least_squares_method = "lm" if use_dense_lm else "trf"
        jacobian = self._dense_jacobian if use_dense_lm else self._jacobian

        for guess in guesses:
            result = least_squares(
                self._objective,
                guess,
                jac=jacobian,
                method=least_squares_method,
                x_scale="jac",
                max_nfev=5000,
            )
            residual_norm = self._residual_norm(result)
            if residual_norm < best_residual_norm:
                best_result = result
                best_residual_norm = residual_norm

            if not result.success or residual_norm > residual_tol:
                continue

            N = self._get_nodes_from_input(result.x)
            if self._is_null_force_solution(N, force_tol, max_zero_force_fraction):
                continue

            self._update_node_positions(N)
            self.tensegrity.update_forces()
            return SolverResult(True, "Solver converged.", result)

        if best_result is not None and best_result.success and best_residual_norm <= residual_tol:
            N = self._get_nodes_from_input(best_result.x)
            if self._is_null_force_solution(N, force_tol, max_zero_force_fraction):
                return SolverResult(
                    False,
                    self._null_force_message(N, force_tol),
                    best_result,
                )

        message = "Solver could not converge."
        if best_result is not None:
            message = f"Solver could not converge: residual norm {best_residual_norm:.3e}; {best_result.message}"

        return SolverResult(False, message, best_result)

    def _refresh_connection_parameters(self) -> None:
        self._connection_stiffness[:] = [
            connection.stiffness for connection in self.tensegrity.connections
        ]
        self._connection_initial_lengths[:] = [
            connection.initial_length for connection in self.tensegrity.connections
        ]

    def _solve_with_root(self, method: str, force_tol: float, max_zero_force_fraction: float) -> SolverResult:
        x0 = self._create_initial_guess()
        result = root(self._objective, x0, method=method) # solver
        if not result.success:
            x0 = x0 + np.random.normal(0, 0.1, len(x0))
            result = root(self._objective, x0, method=method)

            if not result.success:
                return SolverResult(
                    False,
                    f"Solver could not converge: {result.message}",
                    result,
                )

        N = self._get_nodes_from_input(result.x)
        if self._is_null_force_solution(N, force_tol, max_zero_force_fraction):
            return SolverResult(
                False,
                self._null_force_message(N, force_tol),
                result,
            )

        self._update_node_positions(N)
        self.tensegrity.update_forces()

        return SolverResult(True, "Solver converged.", result)

    def _create_initial_guesses(
        self,
        x0: np.ndarray,
        attempts: int,
        perturbation: float,
        random_seed: int,
    ) -> list[np.ndarray]:
        attempts = max(1, attempts)
        guesses = [x0]
        if attempts == 1:
            return guesses

        rng = np.random.default_rng(random_seed)
        scale = perturbation * max(1.0, np.linalg.norm(x0) / np.sqrt(len(x0)))
        for _ in range(attempts - 1):
            guesses.append(x0 + rng.normal(0.0, scale, len(x0)))
        return guesses

    def _residual_norm(self, result) -> float:
        residual = result.fun if hasattr(result, "fun") else self._objective(result.x)
        return float(np.linalg.norm(residual))

    def _update_node_positions(self, N: np.ndarray) -> None:
        # update the positions of the nodes
        for i, node in enumerate(self.tensegrity.nodes):
            position = np.array(node.position, dtype=float)
            position[:self.dim] = N[i]
            node.position = position

    def _is_null_force_solution(
        self,
        N: np.ndarray,
        force_tol: float,
        max_zero_force_fraction: float,
    ) -> bool:
        if not self._expects_internal_force(force_tol):
            return False

        forces = np.array([self._connection_force(connection, N) for connection in self.tensegrity.connections])
        if len(forces) == 0:
            return False

        zero_force_fraction = np.count_nonzero(np.abs(forces) <= force_tol) / len(forces)
        return zero_force_fraction >= max_zero_force_fraction

    def _expects_internal_force(self, force_tol: float) -> bool:
        if np.linalg.norm(self.forces) > force_tol:
            return True

        for connection in self.tensegrity.connections:
            if connection.connection_type != Connection.ConnectionType.STRING:
                continue
            if self._reference_connection_length(connection) > connection.initial_length:
                return True
        return False

    def _reference_connection_length(self, connection: Connection) -> float:
        length = 0
        linked_nodes = self.tensegrity.surface.linked_nodes if self.tensegrity.surface else []
        for i in range(len(connection.nodes_original) - 1):
            node1 = connection.nodes_original[i]
            node2 = connection.nodes_original[i + 1]
            if {node1.name, node2.name} in linked_nodes:
                continue
            length += np.linalg.norm(node1.position[:self.dim] - node2.position[:self.dim])
        return length

    def _connection_force(self, connection: Connection, N: np.ndarray) -> float:
        current_length = self._connection_length(connection, N)
        force = connection.stiffness * (current_length - connection.initial_length)
        if connection.connection_type == Connection.ConnectionType.STRING:
            force = max(0, force)
        return force

    def _null_force_message(self, N: np.ndarray, force_tol: float) -> str:
        forces = np.array([self._connection_force(connection, N) for connection in self.tensegrity.connections])
        zero_force_count = np.count_nonzero(np.abs(forces) <= force_tol)
        max_force = float(np.max(np.abs(forces))) if len(forces) else 0.0
        return (
            "Solver converged to a null-force solution; "
            f"{zero_force_count}/{len(forces)} members are below {force_tol:g} force "
            f"(max |force| {max_force:.3e})."
        )

    # --------------------- INTERNAL FUNCTIONS ---------------------
    def _objective(self, x: np.ndarray) -> np.ndarray:
        """
        Computes the objective function for the optimization problem.
        This function calculates the virtual work from potential energy and external forces,
        and optionally includes surface constraints if a surface is defined.
        
        Args:
            x (np.ndarray): Input array representing the generalized coordinates.
        
        Returns:
            np.ndarray: The objective function value, which is the virtual work with optional surface constraints.
        """
        N = self._get_nodes_from_input(x)
        virtual_work = np.zeros((len(self.tensegrity.nodes), self.dim))

        # Calculate all segment geometry in one batch and scatter local contributions.
        if len(self._segment_starts):
            differences = N[self._segment_starts] - N[self._segment_ends]
            segment_lengths = np.linalg.norm(differences, axis=1)
            segment_lengths[self._seam_segment_mask] = 0.0
            connection_lengths = np.bincount(
                self._segment_connections,
                weights=segment_lengths,
                minlength=len(self.tensegrity.connections),
            )
            coefficients = -self._connection_stiffness * (
                connection_lengths - self._connection_initial_lengths
            )
            slack_strings = (
                self._string_connections
                & (connection_lengths < self._connection_initial_lengths)
            )
            coefficients[slack_strings] = 0.0
            directions = np.zeros_like(differences)
            nonzero = segment_lengths > 0
            directions[nonzero] = (
                differences[nonzero] / segment_lengths[nonzero, np.newaxis]
            )
            contributions = coefficients[self._segment_connections, np.newaxis] * directions
            np.add.at(virtual_work, self._segment_starts, contributions)
            np.add.at(virtual_work, self._segment_ends, -contributions)

        # Virtual work from external forces
        virtual_work = virtual_work.reshape(-1)
        virtual_work += self.forces

        if self.tensegrity.surface:
            for target, source in self._surface_merges:
                virtual_work[target] += virtual_work[source]
            objective = np.concatenate(
                (virtual_work[self._residual_keep_indices], self._surface_constraints_from_nodes(N))
            )

        else:
            objective = virtual_work[self._residual_keep_indices]

        return objective

    def _jacobian(self, x: np.ndarray):
        """Return the sparse analytic Jacobian of the equilibrium residual."""
        N = self._get_nodes_from_input(x)
        jacobian_rows = []
        jacobian_columns = []
        jacobian_values = []

        # The overwhelmingly common two-node member has a compact 2x2 block
        # structure, so assemble all such members without a Python connection loop.
        two_node_ids = self._two_node_connection_ids
        if len(two_node_ids):
            endpoints = np.array(
                [self._connection_indices[index] for index in two_node_ids],
                dtype=np.intp,
            )
            differences = N[endpoints[:, 0]] - N[endpoints[:, 1]]
            lengths = np.linalg.norm(differences, axis=1)
            seam_edges = np.array(
                [self._connection_seam_segments[index][0] for index in two_node_ids],
                dtype=bool,
            )
            lengths[seam_edges] = 0.0
            directions = np.zeros_like(differences)
            nonzero = lengths > 0
            directions[nonzero] = differences[nonzero] / lengths[nonzero, np.newaxis]
            outer_directions = np.einsum("mi,mj->mij", directions, directions)
            stiffness = self._connection_stiffness[two_node_ids]
            coefficient = -stiffness * (
                lengths - self._connection_initial_lengths[two_node_ids]
            )
            active = nonzero & ~(
                self._string_connections[two_node_ids]
                & (lengths < self._connection_initial_lengths[two_node_ids])
            )
            transverse = np.zeros_like(outer_directions)
            transverse[active] = (
                np.eye(self.dim)[np.newaxis, :, :] - outer_directions[active]
            ) / lengths[active, np.newaxis, np.newaxis]
            blocks = (
                -stiffness[:, np.newaxis, np.newaxis] * outer_directions
                + coefficient[:, np.newaxis, np.newaxis] * transverse
            )
            blocks[~active] = 0.0
            coordinates = endpoints[:, :, np.newaxis] * self.dim + np.arange(self.dim)
            for row_endpoint, column_endpoint, sign in (
                (0, 0, 1.0),
                (0, 1, -1.0),
                (1, 0, -1.0),
                (1, 1, 1.0),
            ):
                rows = np.broadcast_to(
                    coordinates[:, row_endpoint, :, np.newaxis],
                    blocks.shape,
                )
                columns = np.broadcast_to(
                    coordinates[:, column_endpoint, np.newaxis, :],
                    blocks.shape,
                )
                jacobian_rows.extend(rows.ravel())
                jacobian_columns.extend(columns.ravel())
                jacobian_values.extend((sign * blocks).ravel())

        # Multi-segment members require coupling all their segment directions.
        for connection_index in self._polyline_connection_ids:
            connection = self.tensegrity.connections[connection_index]
            indices = self._connection_indices[connection_index]
            seam_segments = self._connection_seam_segments[connection_index]
            local_size = len(indices) * self.dim
            length_gradient = np.zeros(local_size)
            length_hessian = np.zeros((local_size, local_size))
            total_length = 0.0

            for segment in range(len(indices) - 1):
                if seam_segments[segment]:
                    continue
                difference = N[indices[segment]] - N[indices[segment + 1]]
                segment_length = float(np.linalg.norm(difference))
                if segment_length == 0.0:
                    continue
                total_length += segment_length
                direction = difference / segment_length
                first = slice(segment * self.dim, (segment + 1) * self.dim)
                second = slice((segment + 1) * self.dim, (segment + 2) * self.dim)
                length_gradient[first] += direction
                length_gradient[second] -= direction
                curvature = (
                    np.eye(self.dim) - np.outer(direction, direction)
                ) / segment_length
                length_hessian[first, first] += curvature
                length_hessian[second, second] += curvature
                length_hessian[first, second] -= curvature
                length_hessian[second, first] -= curvature

            if (
                connection.connection_type == Connection.ConnectionType.STRING
                and total_length < connection.initial_length
            ):
                continue

            coefficient = -connection.stiffness * (
                total_length - connection.initial_length
            )
            local_jacobian = (
                -connection.stiffness
                * np.outer(length_gradient, length_gradient)
                + coefficient * length_hessian
            )
            coordinates = np.array(
                [
                    int(node_index) * self.dim + dimension
                    for node_index in indices
                    for dimension in range(self.dim)
                ],
                dtype=np.intp,
            )
            local_rows, local_columns = np.nonzero(local_jacobian)
            jacobian_rows.extend(coordinates[local_rows])
            jacobian_columns.extend(coordinates[local_columns])
            jacobian_values.extend(local_jacobian[local_rows, local_columns])

        full_jacobian = coo_matrix(
            (jacobian_values, (jacobian_rows, jacobian_columns)),
            shape=(self._coordinate_count, self._coordinate_count),
            dtype=float,
        ).tocsr()
        if self._surface_merges:
            full_jacobian = full_jacobian.tolil()
            for target, source in self._surface_merges:
                full_jacobian[target, :] += full_jacobian[source, :]
            full_jacobian = full_jacobian.tocsr()

        equilibrium_jacobian = full_jacobian[
            self._residual_keep_indices, :
        ][:, self._free_indices]
        if not self._has_cylinder_constraints:
            return equilibrium_jacobian

        constraint_jacobian = lil_matrix(
            (2 * len(self._surface_pairs), len(self._free_indices)),
            dtype=float,
        )
        row = 0
        for node1, node2 in self._surface_pairs:
            y1 = self._free_column.get(node1 * self.dim + 1)
            y2 = self._free_column.get(node2 * self.dim + 1)
            if y1 is not None:
                constraint_jacobian[row, y1] = 1.0
            if y2 is not None:
                constraint_jacobian[row, y2] = -1.0
            row += 1

            difference = N[node1, 0] - N[node2, 0]
            sign = np.sign(difference)
            x1 = self._free_column.get(node1 * self.dim)
            x2 = self._free_column.get(node2 * self.dim)
            if x1 is not None:
                constraint_jacobian[row, x1] = sign
            if x2 is not None:
                constraint_jacobian[row, x2] = -sign
            row += 1

        return vstack((equilibrium_jacobian, constraint_jacobian.tocsr()), format="csr")

    def _dense_jacobian(self, x: np.ndarray) -> np.ndarray:
        """Dense Jacobian adapter for the fast moderate-sized LM solve path."""
        return self._jacobian(x).toarray()

    def _spring_connection_energy(self, connection: Connection, N: np.ndarray) -> float:
        """
        Calculates the energy stored in a spring connection.

        Args:
            connection (Connection): The spring connection object.
            N (np.ndarray): The current positions of all nodes.

        Returns:
            float: The energy stored in the spring connection.
        """
        # current length
        length = self._connection_length(connection, N)

        if connection.connection_type.name == Connection.ConnectionType.STRING.name and length < connection.initial_length:  # string connections cannot store energy when compressed
            return 0

        # energy
        energy = 0.5 * connection.stiffness * (length - connection.initial_length)**2

        return energy

    def _spring_connection_energy_derivative(self, connection: Connection, N: np.ndarray) -> np.ndarray:
        """
        Calculates the derivative of the spring connection energy with respect to node positions.

        The energy of a spring connection is given by:
            V = 0.5 * k * (l - l0)^2
        where k is the stiffness, l is the current length of the connection, and l0 is the rest length.

        The derivative of the energy with respect to the position of node i is:
            dV/dq_i = -k * (l - l0) * dl/dq_i
                    = C * dl/dq_i
        where C is a constant factor.

        Args:
            connection (Connection): The connection object representing the spring.
            N (np.ndarray): The array of node positions.

        Returns:
            np.ndarray: The derivative of the spring connection energy with respect to the node positions.
        """
        # current length
        length = self._connection_length(connection, N)

        if connection.connection_type.name == Connection.ConnectionType.STRING.name and length < connection.initial_length: # string connections cannot store energy when compressed
            return np.zeros(self.dim*len(self.tensegrity.nodes))

        C = -connection.stiffness * (length - connection.initial_length)

        return C * self._length_derivative(connection, N)

    def _length_derivative(self, connection: Connection, N: np.ndarray) -> np.ndarray:
        """
        Calculates the derivative of the length of a connection with respect to the node positions.
        
        Args:
            connection (Connection): The connection object containing the nodes.
            N (np.ndarray): The array of node positions.
        
        Returns:
            np.ndarray: The derivative of the length with respect to the node positions.
        """
        # l = sum_i=1^n-1 ||N_i - N_i+1||

        dl = np.zeros(self.dim*len(self.tensegrity.nodes))

        for i in range(len(connection.nodes) - 1):
            N1_index = self.node_indices[connection.nodes[i].name]
            N2_index = self.node_indices[connection.nodes[i+1].name]
            N1 = N[N1_index]
            N2 = N[N2_index]
            length = self._node_distance(connection.nodes[i].name, connection.nodes[i+1].name, N)
            if length == 0:
                continue
            dl[N1_index*self.dim : N1_index*self.dim + self.dim] += (N1 - N2) / length
            dl[N2_index*self.dim : N2_index*self.dim + self.dim] += (N2 - N1) / length

        return dl

    def _connection_length(self, connection: Connection, N: np.ndarray) -> float:
        """
        Calculates the current length of a connection based on the node positions.

        Args:
            connection (Connection): The connection object.
            N (np.ndarray): The current positions of all nodes.

        Returns:
            float: The current length of the connection.
        """
        length = 0
        for i in range(len(connection.nodes) - 1):
            length += self._node_distance(connection.nodes[i].name, connection.nodes[i+1].name, N)
        return length

    def _node_distance(self, node1: str, node2: str, N: np.ndarray) -> float:
        """
        Calculates the distance between two nodes based on their positions.

        Args:
            node1 (str): The name of the first node.
            node2 (str): The name of the second node.
            N (np.ndarray): The current positions of all nodes.

        Returns:
            float: The distance between the two nodes.
        """
        N1 = N[self.node_indices[node1]]
        N2 = N[self.node_indices[node2]]

        if self.tensegrity.surface:
            if {node1, node2} in self.tensegrity.surface.linked_nodes:
                return 0

        return np.linalg.norm(N1 - N2)

    def _surface_constraints(self, x: np.ndarray) -> np.ndarray:
        """
        Computes the surface constraints for the optimization problem.

        Args:
            x (np.ndarray): The input array representing the current state of the nodes.

        Returns:
            np.ndarray: An array of constraints that must be satisfied. For a cylindrical surface, 
                        the constraints ensure that:
                        - The y-coordinates of linked nodes are equal.
                        - The x-coordinates of linked nodes are exactly the circumference of the cylinder apart.
        """
        return self._surface_constraints_from_nodes(self._get_nodes_from_input(x))

    def _surface_constraints_from_nodes(self, N: np.ndarray) -> np.ndarray:
        constraints = []
        if self.tensegrity.surface.shape["surface_type"] == "cylinder":
            r = self.tensegrity.surface.shape["properties"]["radius"]
            for node1, node2 in self._surface_pairs:
                N1 = N[node1]
                N2 = N[node2]
                constraints.append(N1[1] - N2[1]) # y values must be the same
                constraints.append(np.abs(N1[0] - N2[0]) - 2*np.pi*r) # x values must be exactly the circumference of the cylinder apart

        return np.array(constraints)


    def _create_initial_guess(self) -> np.ndarray:
        """
        Creates the input vector x0 for the optimization problem (node positions - pinned nodes).

        Returns:
            np.ndarray: The input vector x0. 
                        length = d*len(nodes) - pins, Elements are the node positions (except those that are pinned)
        """
        positions = np.array(
            [node.position[:self.dim] for node in self.tensegrity.nodes],
            dtype=float,
        ).reshape(-1)
        return positions[self._free_indices]

    def _get_nodes_from_input(self, x: np.ndarray) -> np.ndarray:
        """
        Extracts node positions input vector (adding the pinned nodes back in).

        Args:
            x (np.ndarray): The input vector containing node positions.

        Returns:
            np.ndarray: The extracted node positions including those removed from the input because they were pinned.
        """
        coordinates = self._pinned_values.copy()
        coordinates[self._free_indices] = x
        return coordinates.reshape(-1, self.dim)
