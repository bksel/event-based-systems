import re
import subprocess

# Sequence of transitions to execute


first_step = "OE__power_on"
order_americano = [
    "OE__order_americano",
    "CE__start_grind",
    "OE__grind_done",
    "CE__heat_to_brew",
    "OE__temp_reached_brew",
    "CE__start_brew",
    "OE__brew_done",
    "CE__add_hot_water",
    "OE__drink_done_americano",
    "CE__eject_grounds",
    "CE__empty_cup",
]

order_espresso = [
    "OE__order_espresso",
    "CE__start_grind",
    "OE__grind_done",
    "CE__heat_to_brew",
    "OE__temp_reached_brew",
    "CE__start_brew",
    "OE__brew_done",
    "OE__drink_done_espresso",
    "CE__eject_grounds",
    "CE__empty_cup",
]

order_cappuccino = [
    "OE__order_cappuccino",
    "CE__start_grind",
    "OE__grind_done",
    "CE__heat_to_brew",
    "OE__temp_reached_brew",
    "CE__start_brew",
    "OE__brew_done",
    "CE__heat_to_steam",
    "OE__temp_reached_steam",
    "CE__start_steam",
    "OE__steam_done",
    "OE__drink_done_cappuccino",
    "CE__eject_grounds",
    "CE__empty_cup",
]

water_error = ["OE__water_empty", "OE__refill_water"]
milk_error = ["OE__milk_empty", "OE__refill_milk"]


sequence = [first_step] + order_americano + order_cappuccino  # + order_espresso
process = subprocess.Popen(
    ["play", "model/model.ndr"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)


def read_state():
    output = []

    while True:
        line = process.stdout.readline()

        if not line:
            break

        output.append(line)

        if "firable:" in line:
            break

    output = "".join(output)

    # Extract current state
    state_match = re.search(r"state \d+:\s*(.*?)firable:", output, re.DOTALL)

    current_state = []

    if state_match:
        for item in state_match.group(1).split():
            if "*" in item:
                place, tokens = item.rsplit("*", 1)
                current_state.append((place, int(tokens)))
            else:
                current_state.append((item, 1))

    # Extract fireable events
    events_match = re.search(r"firable:\s*(.*)", output)

    fireable_events = events_match.group(1).split() if events_match else []

    return current_state, fireable_events


try:
    # Read initial state
    current_state, fireable_events = read_state()

    print("Initial state:")
    print(current_state)
    print("Fireable events:", fireable_events)

    # Execute predefined sequence
    for action in sequence:
        if "CE__heat_to_brew_from_steam" in fireable_events:
            temp = "CE__heat_to_brew_from_steam"
            print(f"\nExecuting: {temp}")
            process.stdin.write(f"f {temp}\n")
            process.stdin.flush()
            current_state, fireable_events = read_state()

        print(f"\nExecuting: {action}")

        if (
            action == "CE__heat_to_brew"
            and any(place == "boiler__brew" for place, tokens in current_state)
            and action not in fireable_events
        ):
            print("Boiler is already hot moving on!")
            continue

        if (
            action == "OE__temp_reached_brew"
            and any(place == "boiler__brew" for place, tokens in current_state)
            and action not in fireable_events
        ):
            print("Boiler is already hot moving on!")
            continue

        if action not in fireable_events:
            print("ERROR: Transition is not fireable!")
            break

        process.stdin.write(f"f {action}\n")
        process.stdin.flush()

        # Read resulting state
        current_state, fireable_events = read_state()
        if action == "CE__empty_cup":
            print("Current state:")
            print(current_state)

            print("Fireable events:")
            print(fireable_events)


finally:
    if process.poll() is None:
        process.stdin.write("q\n")
        process.stdin.flush()
        process.wait()
