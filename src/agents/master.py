def energy_calculation():

    # Get initial energy data (Ideally, these would be retrieved from a data source)
    tec =  None  # Total Energy Consumption
    trec = None  # Total Renewable Energy Consumption

    # 1. Find Total Energy Consumption
    while tec is None:
        tec_input = input("Is Total Energy Consumption (TEC) reported? (Yes/No): ")
        if tec_input.lower() == 'yes':
            while True:
                try:
                    tec = float(input("Enter TEC (in GWh): "))
                    if tec >= 0:  # Validate for non-negativity
                        break
                    else:
                        print("TEC cannot be negative. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a numerical value.")
        elif tec_input.lower() == 'no':
            tec = 711
            break
        else:
            print("Invalid input. Please enter Yes or No.")

    # 2. Find Total Renewable Energy Consumption
    while trec is None:
        trec_input = input("Is Total Renewable Energy Consumption (TREC) reported? (Yes/No): ")
        if trec_input.lower() == 'yes':
            while True:
                try:
                    trec = float(input("Enter TREC (in GWh): "))
                    if trec >= 0:  # Validate for non-negativity
                        break
                    else:
                        print("TREC cannot be negative. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a numerical value.")
        elif trec_input.lower() == 'no':
            # Start Ingredient Collection for Renewable Energy
            trec_ingredients = []
            while True:
                ingredient_available = input("Is a renewable energy ingredient available? (Yes/No): ")
                if ingredient_available.lower() == 'yes':
                    # ... (Logic for collecting and converting ingredient data)
                    pass 
                elif ingredient_available.lower() == 'no':
                    trec = 711
                    break
                else:
                    print("Invalid input. Please enter Yes or No.") 

        else:
            print("Invalid input. Please enter Yes or No.")

    # 3. Calculate Total Non-Renewable Energy Consumption
    if tec != 711 and trec != 711:
        # Start Ingredient Collection for Non-Renewable Energy if needed
        # ... (Similar logic as for renewable energy collection)
        pass

    # 4. Final Aggregation (tnrec = tec - sum of trec_ingredients)
    tnrec = tec - sum(trec_ingredients)

    return tec, trec, tnrec

# --- Example Usage ---
tec_result, trec_result, tnrec_result = energy_calculation()
print("\nResults:")
print(f"Total Energy Consumption (TEC): {tec_result} GWh")
print(f"Total Renewable Energy Consumption (TREC): {trec_result} GWh")
print(f"Total Non-Renewable Energy Consumption (TNREC): {tnrec_result} GWh")
