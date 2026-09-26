"""
Engineering Materials and Physical Mass Properties for SoftWork CAD.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Material:
    """
    Physical engineering material definition with density and elastic properties.
    """
    name: str
    category: str
    density_g_cm3: float  # grams per cubic centimeter
    yield_strength_mpa: float = 250.0
    elastic_modulus_gpa: float = 200.0
    poissons_ratio: float = 0.30

    @property
    def density_kg_m3(self) -> float:
        return self.density_g_cm3 * 1000.0

    def calculate_mass_grams(self, volume_mm3: float) -> float:
        """Calculates mass in grams for a given volume in cubic millimeters."""
        volume_cm3 = volume_mm3 / 1000.0
        return volume_cm3 * self.density_g_cm3


# Standard SolidWorks & Creo Material Library
STANDARD_MATERIALS: Dict[str, Material] = {
    "Plain Carbon Steel 1018": Material("Plain Carbon Steel 1018", "Steel", density_g_cm3=7.85, yield_strength_mpa=370.0, elastic_modulus_gpa=205.0),
    "Stainless Steel 304": Material("Stainless Steel 304", "Steel", density_g_cm3=8.00, yield_strength_mpa=215.0, elastic_modulus_gpa=193.0),
    "Aluminum 6061-T6": Material("Aluminum 6061-T6", "Aluminum", density_g_cm3=2.70, yield_strength_mpa=276.0, elastic_modulus_gpa=68.9),
    "Aluminum 7075-T6": Material("Aluminum 7075-T6", "Aluminum", density_g_cm3=2.81, yield_strength_mpa=503.0, elastic_modulus_gpa=71.7),
    "Brass (Cartridge)": Material("Brass (Cartridge)", "Copper Alloy", density_g_cm3=8.53, yield_strength_mpa=310.0, elastic_modulus_gpa=110.0),
    "Titanium Ti-6Al-4V": Material("Titanium Ti-6Al-4V", "Titanium", density_g_cm3=4.43, yield_strength_mpa=880.0, elastic_modulus_gpa=113.8),
    "ABS Plastic": Material("ABS Plastic", "Polymer", density_g_cm3=1.04, yield_strength_mpa=40.0, elastic_modulus_gpa=2.2),
    "PLA (3D Printing)": Material("PLA (3D Printing)", "Polymer", density_g_cm3=1.24, yield_strength_mpa=50.0, elastic_modulus_gpa=3.5),
    "Nylon 6/6": Material("Nylon 6/6", "Polymer", density_g_cm3=1.14, yield_strength_mpa=80.0, elastic_modulus_gpa=2.8),
}

DEFAULT_MATERIAL = STANDARD_MATERIALS["Aluminum 6061-T6"]
