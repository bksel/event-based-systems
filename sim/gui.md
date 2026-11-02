Inside a graphical interface [name of the program] we are constructing a GUI that gives  a human-friendly view of the coffee machine.

It shows:
## system state:
    - operating mode: m ∈ {off , heating, ready, preparing, ,, descaling} displayed with capital letters - READY
    - state of the resources r:  grinder, pump and steamer ∈ {idle, busy}, boiler ∈ {cold, brew, steam}, brewing unit ∈ {empty, loaded, used(?)}, cup ∈ {absent, present}
    the resources are displayed with different color tones, with respect to their state
    - consumables c: water ∈ {ok, low, empty}, beans and milk ∈ {ok, empty}, grounds counter g ∈ {0, . . . , Ng}, drip tray ∈ {ok, full};
    Consumables are displayed as a rectangle, coloured between 0 and 100 %. 
    - descaling counter: d ∈ {0, . . . , Nover}
    - set of active faults F (can be multiple faults)
## buttons for user events:
    - operation of the machine: power_on ∈ [0, 1], order_espresso, order_americano, order_cappuccino, cup_placed, cup_removed
    Buttons of available drinks are coloured green and the user can click them, while an unavailable drink button is grey-coloured and disables clicking. Drink is unavailable corresponding to a certain fault.
    - services: refill_water, refill_beans,	refill_milk, empty_bin(?), empty_tray,insert_brew_unit, descaling_confirmed, clear_flow_error(?)
    ** the fault events (water_empty, beans_empty, milk_empty, bin_full, grounds container full, tray_full, brew_unit_removed, flow_error(?),overheat(?)) are not supposed to have the buttons that make them happen. Rather, faults will be a result of certain number of ordered coffees that finishes one or more consumables.


