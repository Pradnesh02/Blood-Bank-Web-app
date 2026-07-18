from app.models.blood_stock import BloodStock
from app.models.donor import Donor

# Map of which blood group can donate to which blood groups
COMPATIBILITY_MAP = {
    'O-':  {'can_give_to': ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']},
    'O+':  {'can_give_to': ['A+', 'B+', 'O+', 'AB+']},
    'A-':  {'can_give_to': ['A+', 'A-', 'AB+', 'AB-']},
    'A+':  {'can_give_to': ['A+', 'AB+']},
    'B-':  {'can_give_to': ['B+', 'B-', 'AB+', 'AB-']},
    'B+':  {'can_give_to': ['B+', 'AB+']},
    'AB-': {'can_give_to': ['AB+', 'AB-']},
    'AB+': {'can_give_to': ['AB+']}
}

def get_compatible_alternatives(requested_group, quantity):
    """
    Finds compatible alternative blood groups that have sufficient stock.
    Retrieves all registered fit donors belonging to these compatible blood groups.
    """
    alternatives = []
    
    # Identify compatible groups
    for group, rules in COMPATIBILITY_MAP.items():
        if requested_group in rules['can_give_to']:
            stock = BloodStock.query.filter_by(blood_group=group).first()
            if stock and stock.units >= quantity:
                alternatives.append({
                    'blood_group': group,
                    'available_units': stock.units,
                    'compatibility': 'Full Match' if group == requested_group else 'Compatible Alternative'
                })
                
    # Sort alternatives by unit availability descending
    sorted_alternatives = sorted(alternatives, key=lambda x: x['available_units'], reverse=True)
    
    # Retrieve contact donors for all compatible groups
    compatible_groups = [a['blood_group'] for a in sorted_alternatives]
    donors = Donor.query.filter(
        Donor.blood_group.in_(compatible_groups),
        Donor.health_status == 'Fit'
    ).all()
    
    return {
        'alternatives': sorted_alternatives,
        'contact_donors': [
            {
                'name': d.name,
                'phone': d.phone,
                'blood_group': d.blood_group
            }
            for d in donors
        ]
    }
