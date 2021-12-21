from tbutils.bridgeparts import RawMaterial 
from tbutils.bridgeparts import Material 

def moldingGaugeI(thickness : float, size : float):
    return thickness * 3 * size - thickness*thickness

def lineGauge(ray : float):
    return 3.141592653589793*ray*ray

rawMaterialList = [
    RawMaterial(name = "Asphalt", density = 1020, youngModule = 2.7e10, yieldStrenght = 2.5e6, cost = 0.31, desc = "Material for roads (required)"),
    RawMaterial(name = "Steel", density = 7750, youngModule = 2.0e11, yieldStrenght = 6.5e8, cost = 0.24),
    RawMaterial(name = "Diamond", density = 352, youngModule = 1.2e12, yieldStrenght = 1.6e8, cost = 90.0),
    RawMaterial(name = "Titanum", density = 4507, youngModule = 1.66e11, yieldStrenght = 2.1e8, cost = 1.22),
    RawMaterial(name = "Iron", density = 7870, youngModule = 2.11e11, yieldStrenght = 1.0e8, cost = 0.12),
    RawMaterial(name = "Wood", density = 600, youngModule = 1.0e10, yieldStrenght = 4.0e7, cost = 0.18),
    RawMaterial(name = "Nylon", density = 1150, youngModule = 2.93e9, yieldStrenght = 9.0e8, cost = 1.00),
    ]

rawMaterialDictionary = {material.name: material for material in rawMaterialList}
    
materialList = [
    rawMaterialDictionary["Asphalt"].createMaterial(subname = "Basic road", maxLength = 100.0, gauge = 0.75, line = False),
    rawMaterialDictionary["Asphalt"].createMaterial(subname = "Narrow road", maxLength = 100.0, gauge = 0.55, line = False),
    rawMaterialDictionary["Asphalt"].createMaterial(subname = "Thick road", maxLength = 100.0, gauge = 0.95, line = False),
    
    rawMaterialDictionary["Steel"].createMaterial(subname = "Steel molding 100x15", maxLength = 100.0, gauge = moldingGaugeI(0.015, 0.1), line = False),
    rawMaterialDictionary["Steel"].createMaterial(subname = "Steel molding 200x20", maxLength = 100.0, gauge = moldingGaugeI(0.020, 0.2), line = False),
    rawMaterialDictionary["Steel"].createMaterial(subname = "Steel molding 300x25", maxLength = 100.0, gauge = moldingGaugeI(0.025, 0.3), line = False),
    rawMaterialDictionary["Steel"].createMaterial(subname = "Steel molding 500x45", maxLength = 100.0, gauge = moldingGaugeI(0.045, 0.5), line = False),
        
    rawMaterialDictionary["Titanum"].createMaterial(subname = "Titanum molding 100x15", maxLength = 100.0, gauge = moldingGaugeI(0.015, 0.1), line = False),
    rawMaterialDictionary["Titanum"].createMaterial(subname = "Titanum molding 200x20", maxLength = 100.0, gauge = moldingGaugeI(0.020, 0.2), line = False),
    rawMaterialDictionary["Titanum"].createMaterial(subname = "Titanum molding 300x25", maxLength = 100.0, gauge = moldingGaugeI(0.025, 0.3), line = False),
    rawMaterialDictionary["Titanum"].createMaterial(subname = "Titanum molding 500x45", maxLength = 100.0, gauge = moldingGaugeI(0.045, 0.5), line = False),
        
    rawMaterialDictionary["Iron"].createMaterial(subname = "Iron molding 100x15", maxLength = 100.0, gauge = moldingGaugeI(0.015, 0.1), line = False),
    rawMaterialDictionary["Iron"].createMaterial(subname = "Iron molding 200x20", maxLength = 100.0, gauge = moldingGaugeI(0.020, 0.2), line = False),
    rawMaterialDictionary["Iron"].createMaterial(subname = "Iron molding 300x25", maxLength = 100.0, gauge = moldingGaugeI(0.025, 0.3), line = False),
    rawMaterialDictionary["Iron"].createMaterial(subname = "Iron molding 500x45", maxLength = 100.0, gauge = moldingGaugeI(0.045, 0.5), line = False),
    
    rawMaterialDictionary["Diamond"].createMaterial(subname = "Diamond molding 100x15", maxLength = 100.0, gauge = moldingGaugeI(0.015, 0.1), line = False),
    rawMaterialDictionary["Diamond"].createMaterial(subname = "Diamond molding 200x20", maxLength = 100.0, gauge = moldingGaugeI(0.020, 0.2), line = False),
    rawMaterialDictionary["Diamond"].createMaterial(subname = "Diamond molding 300x25", maxLength = 100.0, gauge = moldingGaugeI(0.025, 0.3), line = False),
    rawMaterialDictionary["Diamond"].createMaterial(subname = "Diamond molding 500x45", maxLength = 100.0, gauge = moldingGaugeI(0.045, 0.5), line = False),
        
    rawMaterialDictionary["Wood"].createMaterial(subname = "Wood molding 100x100", maxLength = 100.0, gauge = 0.100*0.100, line = False),
    rawMaterialDictionary["Wood"].createMaterial(subname = "Wood molding 150x150", maxLength = 100.0, gauge = 0.150*0.150, line = False),
    rawMaterialDictionary["Wood"].createMaterial(subname = "Wood molding 200x200", maxLength = 100.0, gauge = 0.200*0.200, line = False),
    rawMaterialDictionary["Wood"].createMaterial(subname = "Wood molding 250x250", maxLength = 100.0, gauge = 0.250*0.250, line = False),
    rawMaterialDictionary["Wood"].createMaterial(subname = "Wood molding 500x500", maxLength = 100.0, gauge = 0.500*0.500, line = False),
    rawMaterialDictionary["Wood"].createMaterial(subname = "Wood molding 1000x1000", maxLength = 100.0, gauge = 1.000*1.000, line = False),
    
    rawMaterialDictionary["Steel"].createMaterial(subname = "Steel line 20", maxLength = 150.0, gauge = lineGauge(0.020), line = True),
    rawMaterialDictionary["Steel"].createMaterial(subname = "Steel line 30", maxLength = 150.0, gauge = lineGauge(0.030), line = True),
    rawMaterialDictionary["Steel"].createMaterial(subname = "Steel line 50", maxLength = 150.0, gauge = lineGauge(0.050), line = True),
    rawMaterialDictionary["Steel"].createMaterial(subname = "Steel line 80", maxLength = 150.0, gauge = lineGauge(0.080), line = True),
    rawMaterialDictionary["Steel"].createMaterial(subname = "Steel line 100", maxLength = 150.0, gauge = lineGauge(0.100), line = True),
    rawMaterialDictionary["Steel"].createMaterial(subname = "Steel line 200", maxLength = 150.0, gauge = lineGauge(0.200), line = True),
    rawMaterialDictionary["Steel"].createMaterial(subname = "Steel line 300", maxLength = 150.0, gauge = lineGauge(0.300), line = True),
    rawMaterialDictionary["Steel"].createMaterial(subname = "Steel line 500", maxLength = 150.0, gauge = lineGauge(0.500), line = True),
    rawMaterialDictionary["Steel"].createMaterial(subname = "Steel line 800", maxLength = 150.0, gauge = lineGauge(0.800), line = True),
    rawMaterialDictionary["Steel"].createMaterial(subname = "Steel line 1000", maxLength = 150.0, gauge = lineGauge(0.1000), line = True),
    
    rawMaterialDictionary["Nylon"].createMaterial(subname = "Nylon line 20", maxLength = 150.0, gauge = lineGauge(0.020), line = True),
    rawMaterialDictionary["Nylon"].createMaterial(subname = "Nylon line 30", maxLength = 150.0, gauge = lineGauge(0.030), line = True),
    rawMaterialDictionary["Nylon"].createMaterial(subname = "Nylon line 50", maxLength = 150.0, gauge = lineGauge(0.050), line = True),
    rawMaterialDictionary["Nylon"].createMaterial(subname = "Nylon line 80", maxLength = 150.0, gauge = lineGauge(0.080), line = True),
    rawMaterialDictionary["Nylon"].createMaterial(subname = "Nylon line 100", maxLength = 150.0, gauge = lineGauge(0.100), line = True),
    rawMaterialDictionary["Nylon"].createMaterial(subname = "Nylon line 200", maxLength = 150.0, gauge = lineGauge(0.200), line = True),
    rawMaterialDictionary["Nylon"].createMaterial(subname = "Nylon line 300", maxLength = 150.0, gauge = lineGauge(0.300), line = True),
    rawMaterialDictionary["Nylon"].createMaterial(subname = "Nylon line 500", maxLength = 150.0, gauge = lineGauge(0.500), line = True),
    rawMaterialDictionary["Nylon"].createMaterial(subname = "Nylon line 800", maxLength = 150.0, gauge = lineGauge(0.800), line = True),
    rawMaterialDictionary["Nylon"].createMaterial(subname = "Nylon line 1000", maxLength = 150.0, gauge = lineGauge(0.1000), line = True),
    ]

materialDictionary = {material.name: material for material in materialList}
