from src.generate.load_ingredients import load_energy_data
from src.generate.load_ingredients import EnergyData
from src.config.logging import logger
import json 



try:
    with open('./data/output/ingredients.txt', 'r') as f:
        data = json.load(f)
        logger.info("Data successfully loaded.")
        print(type(data))
        
except FileNotFoundError:
    logger.error("Failed to find the specified file.")
except Exception as e:
    print(e)

print(data['final_answer'])
print('\n' * 100)
# Create an instance of EnergyData
energy_data = EnergyData(data['year'], data['metrics'], data['metadata'])

# Example of using the new classes
print(f"Energy Data Year: {energy_data.year}")
print("Sources:", energy_data.metadata['data_sources'])

print("\nRenewable Energy Items:")
for item in energy_data.renewable_energy:
    print(item.display_details())

print("\nNon-Renewable Energy Items:")
for item in energy_data.non_renewable_energy:
    print(item.display_details())