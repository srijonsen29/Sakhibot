import json
from pathlib import Path

class ResourceLocator:
    """Agent 3: Finds helplines, shelters, and One Stop Centres"""
    
    def __init__(self):
        self.resources_path = Path("data/resources.json")
        self.resources = self._load_resources()
    
    def _load_resources(self):
        """Load resources from JSON file"""
        if not self.resources_path.exists():
            return {"helplines": [], "one_stop_centres": {}, "shelters": {}}
        
        with open(self.resources_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_helplines(self):
        """Get all emergency helplines"""
        return self.resources.get("helplines", [])
    
    def get_emergency_contacts(self):
        """Get critical emergency numbers"""
        helplines = self.get_helplines()
        emergency = [h for h in helplines if h['number'] in ['181', '100']]
        return emergency
    
    def find_one_stop_centres(self, city: str = None):
        """Find One Stop Centres by city"""
        centres = self.resources.get("one_stop_centres", {})
        
        if city:
            city_key = self._normalize_city(city)
            return centres.get(city_key, [])
        
        return centres
    
    def find_shelters(self, city: str = None):
        """Find women's shelters by city"""
        shelters = self.resources.get("shelters", {})
        
        if city:
            city_key = self._normalize_city(city)
            return shelters.get(city_key, [])
        
        return shelters
    
    def _normalize_city(self, city: str):
        """Normalize city name for lookup"""
        city_map = {
            "delhi": "Delhi",
            "mumbai": "Mumbai",
            "bangalore": "Bangalore",
            "bengaluru": "Bangalore",
            "kolkata": "Kolkata",
            "calcutta": "Kolkata"
        }
        return city_map.get(city.lower(), city.title())
    
    def get_all_resources(self, city: str = None):
        """Get comprehensive resource list"""
        return {
            "helplines": self.get_helplines(),
            "one_stop_centres": self.find_one_stop_centres(city),
            "shelters": self.find_shelters(city),
            "city": city or "All India"
        }
    
    def format_emergency_card(self):
        """Format emergency contact card for quick access"""
        emergency = self.get_emergency_contacts()
        
        card = "🚨 EMERGENCY CONTACTS\n\n"
        for contact in emergency:
            card += f"📞 {contact['name']}: {contact['number']}\n"
            card += f"   {contact['description']}\n\n"
        
        return card
