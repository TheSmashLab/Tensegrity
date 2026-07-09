import argparse

from TensegritySim import TensegrityError, TensegrityInputError, YamlParser, Visualization, TensegritySolver


def infer_visualization_dimension(tensegrity_system):
    """Infer whether a parsed tensegrity system should be solved and shown in 2D or 3D."""
    if tensegrity_system.surface:
        return 3

    for node in tensegrity_system.nodes:
        if len(node.position) >= 3 and abs(node.position[2]) > 1e-9:
            return 3

    for pin_state in tensegrity_system.pins.values():
        if len(pin_state) >= 3 and pin_state[2]:
            return 3

    return 2


def _print_requested_positions(tensegrity_system):
    if not tensegrity_system.positions:
        return

    nodes_by_name = {node.name: node for node in tensegrity_system.nodes}
    for node_name in tensegrity_system.positions:
        if node_name not in nodes_by_name:
            print(f"Position request skipped: unknown node {node_name}.")
            continue
        node = nodes_by_name[node_name]
        position = ", ".join(f"{value:.3f}" for value in node.position)
        print(f"{node_name}: ({position})")


def _parse_control_input(user_input, expected_count):
    try:
        delta_lengths = [float(delta.strip()) for delta in user_input.split(",")]
    except ValueError as exc:
        raise TensegrityInputError("Control changes must be numeric values.") from exc

    if len(delta_lengths) != expected_count:
        raise TensegrityInputError(f"Expected {expected_count} control value(s), got {len(delta_lengths)}.")

    return delta_lengths


def _solve_and_plot(solver, viz, tensegrity_system, show_forces=False):
    result = solver.solve()
    if not result.success:
        print(result.message)
        print("Structure was left unchanged.")
        return False

    viz.plot(label_nodes=False, label_connections=True, label_forces=show_forces)
    _print_requested_positions(tensegrity_system)
    return True


def main(file):
    try:
        # Load the tensegrity system from the YAML file
        tensegrity_system = YamlParser.parse(file)

        # Create the visualization object
        viz = Visualization(tensegrity_system, dim=infer_visualization_dimension(tensegrity_system))


        # Plot the initial tensegrity system
        viz.plot(label_nodes=False, label_connections=True)

        # Solve the tensegrity system
        solver = TensegritySolver(tensegrity_system, dim=viz.dim)
        _solve_and_plot(solver, viz, tensegrity_system)
    except TensegrityError as exc:
        print(f"Error: {exc}")
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}")
        return 1

    show_forces = False

    print("Enter 'q' to quit.")
    print("Enter 'r' to reset control lengths.")
    print("Enter 'f' to show/hide forces.")
    if len(tensegrity_system.controls) == 1:
        print(f"Enter changes in length to control {tensegrity_system.get_control_order()} to update simulation.")
    else:
        print(f"Enter changes in length to control strings as comma-separated values in the order of: {tensegrity_system.get_control_order()} to update simulation.")

    while True:
        user_input = input("Input: ")
        if user_input == "q":
            break
        elif user_input == "r":
            tensegrity_system.reset_control_lengths()
        elif user_input == "f":
            show_forces = not show_forces
            viz.plot(label_nodes=False, label_connections=True, label_forces=show_forces)
            continue
        else:
            try:
                delta_lengths = _parse_control_input(user_input, len(tensegrity_system.controls))
                tensegrity_system.change_control_lengths(*delta_lengths)
            except TensegrityError as exc:
                print(f"Input error: {exc}")
                continue

        _solve_and_plot(solver, viz, tensegrity_system, show_forces=show_forces)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tensegrity Simulator")
    parser.add_argument("filename", help="YAML file to load", default="yaml/1-box.yaml")

    args = vars(parser.parse_args())
    raise SystemExit(main(file=args["filename"]))
