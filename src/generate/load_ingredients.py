from src.config.logging import logger
from typing import Dict, List
import json

class EnergyConsumption:
    """
    Represents energy consumption data.
    
    Attributes:
        code (int): Unique code for the energy item.
        item (str): Description of the energy item.
        value (float): Quantity of energy consumed.
        unit (str): Unit of measurement for the energy value.
        page_number (int): Page number in the document where the data is found.
        snippet (str): Text snippet containing the energy data.
    """
    
    def __init__(self, code: int, item: str, value: float, unit: str, page_number: int, snippet: str):
        self.code = code
        self.item = item
        self.value = value
        self.unit = unit
        self.page_number = page_number
        self.snippet = snippet

class RenewableEnergy(EnergyConsumption):
    """
    Subclass for renewable energy consumption data.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.energy_type = "Renewable"

    def display_details(self) -> str:
        return f"{self.item} ({self.energy_type}) - {self.value} {self.unit}"

class NonRenewableEnergy(EnergyConsumption):
    """
    Subclass for non-renewable energy consumption data.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.energy_type = "Non-Renewable"

    def display_details(self) -> str:
        return f"{self.item} ({self.energy_type}) - {self.value} {self.unit}"

class EnergyData:
    """
    Organizes and manages energy data by year with associated metadata.
    
    Attributes:
        year (int): Year of the energy data.
        metadata (Dict[str, str]): Additional information about the energy data.
        renewable_energy (List[RenewableEnergy]): List of renewable energy instances.
        non_renewable_energy (List[NonRenewableEnergy]): List of non-renewable energy instances.
    """
    
    def __init__(self, year: int, metrics: Dict[str, List[Dict]], metadata: Dict[str, str]):
        self.year = year
        self.metadata = metadata
        renewable_codes = [772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 848, 849]
        non_renewable_codes = [785, 786, 787, 789, 783]

        self.renewable_energy = [
            RenewableEnergy(**item) if item['code'] in renewable_codes else RenewableEnergy(code=item['code'], item='Generic Renewable', value=0, unit='units', page_number=0, snippet='No specific data')
            for item in metrics['renewable_energy_consumption']
        ]

        self.non_renewable_energy = [
            NonRenewableEnergy(**item) if item['code'] in non_renewable_codes else NonRenewableEnergy(code=item['code'], item='Generic Non-Renewable', value=0, unit='units', page_number=0, snippet='No specific data')
            for item in metrics['non_renewable_energy_consumption']
        ]

def load_energy_data():
    """
    Loads energy data from a JSON file, handling file not found and decode errors.
    """
    try:
        with open('./data/output/ingredients.txt', 'r') as f:
            data = json.load(f)
            logger.info("Data successfully loaded.")
            print(data)
    except FileNotFoundError:
        logger.error("Failed to find the specified file.")
    except json.JSONDecodeNameError:
        logger.error("Failed to decode JSON from the file.")
