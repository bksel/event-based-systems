
import subprocess
import re

# Sequence of transitions to execute



first_step = 'CE__power__on'
order_americano = ['CE__order_americano','CE__grind__start','OE__grind__end','CE__heating_to_brew',
                   'heating_to_brew_end', 'CE__brewing_start','OE__brewing_end',
                   'CE__add_hot_woter', 'OE__americano_done','CE__eject_grounds', 'CE__cup_empty']

order_espresso = ['CE__order_espresso','CE__grind__start','OE__grind__end','CE__heating_to_brew',
                  'heating_to_brew_end','CE__brewing_start','OE__brewing_end', 'OE__espresso_done',
                  'CE__eject_grounds','CE__cup_empty']

order_cappuccino = ['CE_order_cappucino','CE__grind__start','OE__grind__end','CE__heating_to_brew',
                     'heating_to_brew_end','CE__brewing_start','OE__brewing_end','CE__heating_to_steam',
                     'heating_to_steam_end', 'CE__steam_start', 'OE__steam_end', 'OE__cappucino_done',
                     'CE__eject_grounds','CE__cup_empty']

water_error = ['OE__water_empty', 'CE__water_refill']
milk_error = ['OE__mile_empty', 'CE__milk_refill']


sequence = [first_step] +order_americano + order_cappuccino  #+ order_espresso
process = subprocess.Popen(
    ["play", "model/model.ndr"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
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
    state_match = re.search(
        r"state \d+:\s*(.*?)firable:",
        output,
        re.DOTALL
    )

    current_state = []

    if state_match:
        for item in state_match.group(1).split():
            if "*" in item:
                place, tokens = item.rsplit("*", 1)
                current_state.append((place, int(tokens)))
            else:
                current_state.append((item, 1))

    # Extract fireable events
    events_match = re.search(
        r"firable:\s*(.*)",
        output
    )

    fireable_events = (
        events_match.group(1).split()
        if events_match else []
    )

    return current_state, fireable_events


try:
    # Read initial state
    current_state, fireable_events = read_state()

    print("Initial state:")
    print(current_state)
    print("Fireable events:", fireable_events)

    # Execute predefined sequence
    for action in sequence:

        if 'CE__cooling_to_brew' in fireable_events:
                    temp = 'CE__cooling_to_brew'
                    print(f"\nExecuting: {temp}")
                    process.stdin.write(f"f {temp}\n")
                    process.stdin.flush()
                    current_state, fireable_events = read_state()
                    


        print(f"\nExecuting: {action}")

        if  (action == 'CE__heating_to_brew' and any(place == 'boiler__brew' for place, tokens in current_state)
             and action not in fireable_events):
            print("Boiler is already hot moving on!")
            continue
                
        if  (action == 'heating_to_brew_end' and any(place == 'boiler__brew' for place, tokens in current_state)
             and action not in fireable_events):
            print("Boiler is already hot moving on!")
            continue
        
        if action not in fireable_events:
            print("ERROR: Transition is not fireable!")
            break

        process.stdin.write(f"f {action}\n")
        process.stdin.flush()

        # Read resulting state
        current_state, fireable_events = read_state()
        if action == 'CE__cup_empty':
            print("Current state:")
            print(current_state)

            print("Fireable events:")
            print(fireable_events)
            

finally:
    if process.poll() is None:
        process.stdin.write("q\n")
        process.stdin.flush()
        process.wait()
