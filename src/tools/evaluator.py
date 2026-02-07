"""Evaluate and score manufacturers against search criteria.

Scoring Philosophy: "Reward what you find, never penalize what's missing."
Missing data = 0 points (not negative). Only award points for positive signals discovered.
"""

from typing import Any, Dict, List, Optional

from rich.console import Console

from models.criteria import SearchCriteria
from models.manufacturer import Manufacturer

console = Console()

# ---------------------------------------------------------------------------
# Region mapping for location scoring
# ---------------------------------------------------------------------------
REGION_MAP = {
    "southeast asia": [
        "vietnam", "thailand", "indonesia", "cambodia", "myanmar",
        "philippines", "malaysia", "laos", "singapore",
    ],
    "east asia": [
        "china", "japan", "south korea", "korea", "taiwan", "hong kong", "macau",
    ],
    "south asia": [
        "india", "bangladesh", "sri lanka", "pakistan", "nepal",
    ],
    "north america": [
        "usa", "united states", "us", "canada", "mexico",
    ],
    "central america": [
        "guatemala", "honduras", "el salvador", "nicaragua", "costa rica", "panama",
    ],
    "south america": [
        "brazil", "colombia", "peru", "argentina", "chile", "ecuador",
    ],
    "western europe": [
        "portugal", "spain", "italy", "france", "germany", "uk",
        "united kingdom", "england", "ireland", "netherlands", "belgium",
        "switzerland", "austria", "denmark", "sweden", "norway", "finland",
    ],
    "eastern europe": [
        "turkey", "poland", "romania", "czech republic", "hungary",
        "bulgaria", "croatia", "serbia",
    ],
    "north africa": ["morocco", "tunisia", "egypt"],
    "sub-saharan africa": [
        "ethiopia", "kenya", "madagascar", "mauritius", "south africa",
        "tanzania", "uganda", "ghana", "nigeria",
    ],
    "middle east": [
        "uae", "united arab emirates", "jordan", "israel",
        "saudi arabia", "bahrain", "qatar", "oman",
    ],
    "oceania": ["australia", "new zealand", "fiji"],
}

# Trade partners for "reasonable alternative" scoring
TRADE_PARTNERS = {
    "usa": ["mexico", "canada", "guatemala", "honduras", "dominican republic"],
    "united states": ["mexico", "canada", "guatemala", "honduras"],
    "us": ["mexico", "canada", "guatemala", "honduras"],
    "china": ["vietnam", "bangladesh", "india", "cambodia"],
    "vietnam": ["china", "thailand", "cambodia", "indonesia"],
    "bangladesh": ["india", "sri lanka", "vietnam"],
    "india": ["bangladesh", "sri lanka", "vietnam"],
    "portugal": ["spain", "italy", "morocco", "turkey"],
    "italy": ["portugal", "spain", "turkey", "romania"],
    "turkey": ["italy", "portugal", "bulgaria", "romania", "morocco"],
    "mexico": ["usa", "united states", "guatemala", "honduras"],
    "canada": ["usa", "united states"],
    "thailand": ["vietnam", "cambodia", "indonesia", "myanmar"],
    "indonesia": ["vietnam", "thailand", "cambodia"],
    "cambodia": ["vietnam", "thailand", "china"],
}

# ---------------------------------------------------------------------------
# Certification point values
# ---------------------------------------------------------------------------
CERT_POINTS = {
    "oeko-tex": 8, "oeko-tex standard 100": 8, "oeko-tex 100": 8, "oeko tex": 8,
    "gots": 8, "global organic textile standard": 8,
    "fair trade": 7, "fair trade certified": 7, "fairtrade": 7,
    "bluesign": 7,
    "wrap": 6, "worldwide responsible accredited production": 6,
    "sa8000": 6, "social accountability": 6, "sa 8000": 6,
    "iso 9001": 5, "iso9001": 5,
    "iso 14001": 5, "iso14001": 5,
    "better cotton": 5, "bci": 5, "better cotton initiative": 5,
    "cradle to cradle": 6, "c2c": 6,
}
DEFAULT_CERT_POINTS = 4
WORKING_TOWARDS_POINTS = 3
MENTIONS_STANDARDS_POINTS = 2

# ---------------------------------------------------------------------------
# Material families for similarity matching
# ---------------------------------------------------------------------------
MATERIAL_FAMILIES = {
    "polyester": [
        "recycled polyester", "rpet", "repreve", "polyester", "pet", "recycled pet",
    ],
    "cotton": [
        "organic cotton", "cotton", "bci cotton", "pima cotton", "supima cotton",
    ],
    "nylon": [
        "nylon", "recycled nylon", "econyl", "polyamide", "nylon 6", "nylon 66",
    ],
    "spandex": ["spandex", "elastane", "lycra"],
    "bamboo": ["bamboo", "bamboo viscose", "bamboo lyocell", "bamboo fiber"],
    "tencel": ["tencel", "lyocell", "modal"],
    "merino": ["merino wool", "merino", "wool", "fine merino"],
    "silk": ["silk", "mulberry silk"],
}
SUSTAINABLE_MATERIAL_KEYWORDS = [
    "recycled", "organic", "eco", "sustainable", "biodegradable",
    "plant-based", "hemp", "bamboo", "tencel",
]
PREMIUM_MATERIAL_KEYWORDS = [
    "merino", "cashmere", "silk", "graphene", "coolmax",
    "cordura", "gore-tex", "supplex",
]

# ---------------------------------------------------------------------------
# Production method families for similarity matching
# ---------------------------------------------------------------------------
METHOD_FAMILIES = {
    "sublimation": [
        "sublimation printing", "sublimation", "dye sublimation", "dye-sublimation",
    ],
    "screen printing": [
        "screen printing", "silk screen", "silkscreen", "screen print",
    ],
    "digital printing": ["digital printing", "dtg", "direct to garment"],
    "cut and sew": [
        "cut-and-sew", "cut and sew", "cmt", "cut make trim", "cut & sew",
    ],
    "seamless knitting": ["seamless knitting", "seamless", "seamless construction"],
    "circular knitting": ["circular knitting", "circular knit"],
    "warp knitting": ["warp knitting", "warp knit"],
    "knitting": ["knitting", "flat knitting", "flatbed knitting"],
    "printing": [
        "sublimation", "screen printing", "digital printing",
        "heat transfer", "heat press",
    ],
    "finishing": [
        "anti-microbial", "antimicrobial", "moisture wicking",
        "anti-shrink", "dwr", "water repellent",
    ],
    "dyeing": ["dyeing", "garment dyeing", "piece dyeing", "yarn dyeing", "dye"],
    "embroidery": ["embroidery", "embroidered"],
    "laser cutting": ["laser cutting", "laser cut"],
}
FULL_SERVICE_KEYWORDS = [
    "full service", "full-service", "complete production", "full package",
    "fpp", "one-stop", "turnkey", "end-to-end",
]


class Evaluator:
    """Evaluates manufacturers against search criteria and assigns match scores.

    Scoring breakdown (0-100 base + bonuses, capped at 100):
    - Location match: 25 points
    - MOQ compatibility: 20 points
    - Certifications: 25 points (stackable)
    - Materials capability: 15 points
    - Production methods: 15 points
    - Bonus points: variable (website quality, credibility, contact info)
    """

    def __init__(self):
        """Initialize the evaluator."""
        pass

    def evaluate(
        self, manufacturers: List[Manufacturer], criteria: SearchCriteria
    ) -> List[Manufacturer]:
        """
        Evaluate manufacturers against criteria and assign match scores.

        Args:
            manufacturers: List of Manufacturer objects to evaluate
            criteria: SearchCriteria to evaluate against

        Returns:
            List of Manufacturer objects with updated match_score, confidence, and notes
        """
        console.print(
            f"\n[bold cyan]Step 6: Evaluating Manufacturers[/bold cyan] ({len(manufacturers)} candidates)\n"
        )

        for manufacturer in manufacturers:
            breakdown = self._score_manufacturer(manufacturer, criteria)

            # Sum base categories
            base_score = (
                breakdown["location"]["score"]
                + breakdown["moq"]["score"]
                + breakdown["certifications"]["score"]
                + breakdown["materials"]["score"]
                + breakdown["production"]["score"]
            )
            bonus_score = breakdown["bonuses"]["score"]
            conflict_deduction = breakdown.get("conflict_deduction", 0)

            # Cap at 100, floor at 0
            final_score = min(100.0, max(0.0, base_score + bonus_score - conflict_deduction))

            manufacturer.match_score = round(final_score, 1)
            manufacturer.confidence = self._assess_confidence(manufacturer)
            manufacturer.notes = self._generate_breakdown(
                manufacturer, breakdown, base_score, bonus_score,
                conflict_deduction, final_score,
            )

        # Sort by match score (descending)
        manufacturers.sort(key=lambda m: m.match_score, reverse=True)

        # Display top matches
        console.print("[bold]Top Matches:[/bold]")
        for i, mfr in enumerate(manufacturers[:5], 1):
            console.print(
                f"  {i}. {mfr.name} - [green]{mfr.match_score}[/green] ({mfr.confidence})"
            )
        console.print()

        return manufacturers

    # ------------------------------------------------------------------
    # Internal scoring orchestration
    # ------------------------------------------------------------------

    def _score_manufacturer(
        self, manufacturer: Manufacturer, criteria: SearchCriteria
    ) -> Dict[str, Any]:
        """Score a single manufacturer across all categories."""
        return {
            "location": self._score_location(manufacturer, criteria),
            "moq": self._score_moq(manufacturer, criteria),
            "certifications": self._score_certifications(manufacturer, criteria),
            "materials": self._score_materials(manufacturer, criteria),
            "production": self._score_production_methods(manufacturer, criteria),
            "bonuses": self._score_bonuses(manufacturer),
            "conflict_deduction": 0,
        }

    # ------------------------------------------------------------------
    # 1. Location (0-25 points)
    # ------------------------------------------------------------------

    def _score_location(
        self, manufacturer: Manufacturer, criteria: SearchCriteria
    ) -> Dict[str, Any]:
        """
        Score location match (0-25 points).

        - Exact match to preferred locations: 25 pts
        - Same region (e.g., both Southeast Asia): 18 pts
        - Reasonable alternative (trade partner): 12 pts
        - Any location clearly stated: 8 pts
        - Location unknown: 0 pts (not penalized)
        """
        result: Dict[str, Any] = {"score": 0.0, "detail": "", "max": 25}

        if not criteria.locations:
            result["score"] = 25.0
            result["detail"] = "No location preference (full points)"
            return result

        if not manufacturer.location:
            result["detail"] = "Location unknown"
            return result

        mfr_location = manufacturer.location.lower()

        # Exact match
        for pref in criteria.locations:
            if pref.lower() in mfr_location or mfr_location in pref.lower():
                result["score"] = 25.0
                result["detail"] = f"{manufacturer.location} (exact match)"
                return result

        # Same region
        mfr_region = self._get_region(mfr_location)
        for pref in criteria.locations:
            pref_region = self._get_region(pref.lower())
            if mfr_region and pref_region and mfr_region == pref_region:
                result["score"] = 18.0
                result["detail"] = f"{manufacturer.location} (same region: {mfr_region})"
                return result

        # Trade partner / reasonable alternative
        for pref in criteria.locations:
            partners = TRADE_PARTNERS.get(pref.lower(), [])
            for partner in partners:
                if partner in mfr_location or mfr_location in partner:
                    result["score"] = 12.0
                    result["detail"] = f"{manufacturer.location} (trade partner of {pref})"
                    return result

        # Location stated but not preferred
        result["score"] = 8.0
        result["detail"] = f"{manufacturer.location} (stated, not preferred)"
        return result

    @staticmethod
    def _get_region(location: str) -> Optional[str]:
        """Return the region name a location belongs to, or None."""
        loc = location.lower()
        for region, countries in REGION_MAP.items():
            for country in countries:
                if country in loc or loc in country:
                    return region
        return None

    # ------------------------------------------------------------------
    # 2. MOQ Compatibility (0-20 points)
    # ------------------------------------------------------------------

    def _score_moq(
        self, manufacturer: Manufacturer, criteria: SearchCriteria
    ) -> Dict[str, Any]:
        """
        Score MOQ compatibility (0-20 points).

        - Within user's specified range: 20 pts
        - Close to range (±30% outside): 15 pts
        - States "Flexible MOQ" or "Negotiable": 12 pts
        - States "Low MOQ" (when user wants low): 10 pts
        - States "Small orders welcome": 8 pts
        - Any MOQ stated (transparent but not ideal): 5 pts
        - MOQ unknown: 0 pts (not penalized)
        """
        result: Dict[str, Any] = {"score": 0.0, "detail": "", "max": 20}

        if criteria.moq_min is None and criteria.moq_max is None:
            result["score"] = 20.0
            result["detail"] = "No MOQ preference (full points)"
            return result

        # Check text-based MOQ description first
        moq_desc = manufacturer.moq_description
        if moq_desc:
            desc_lower = moq_desc.lower()
            if any(kw in desc_lower for kw in ["flexible", "negotiable"]):
                result["score"] = 12.0
                result["detail"] = f"'{moq_desc}' (flexible MOQ)"
                return result
            if "low moq" in desc_lower or "low minimum" in desc_lower:
                wants_low = criteria.moq_max is not None and criteria.moq_max <= 1000
                result["score"] = 10.0 if wants_low else 8.0
                result["detail"] = f"'{moq_desc}' (low MOQ)"
                return result
            if "small order" in desc_lower:
                result["score"] = 8.0
                result["detail"] = f"'{moq_desc}' (small orders welcome)"
                return result

        if manufacturer.moq is None:
            result["detail"] = "MOQ unknown"
            return result

        moq = manufacturer.moq
        moq_min = criteria.moq_min or 0
        moq_max = criteria.moq_max or float("inf")

        # Within range
        if moq_min <= moq <= moq_max:
            result["score"] = 20.0
            result["detail"] = f"{moq:,} units (within range)"
            return result

        # Close to range (±30%)
        buffer_low = moq_min * 0.7 if moq_min else 0
        buffer_high = moq_max * 1.3 if moq_max != float("inf") else float("inf")

        if buffer_low <= moq <= buffer_high:
            result["score"] = 15.0
            result["detail"] = f"{moq:,} units (close to range)"
            return result

        # Stated but far from range
        result["score"] = 5.0
        result["detail"] = f"{moq:,} units (stated, outside range)"
        return result

    # ------------------------------------------------------------------
    # 3. Certifications (0-25 points, stackable)
    # ------------------------------------------------------------------

    def _score_certifications(
        self, manufacturer: Manufacturer, criteria: SearchCriteria
    ) -> Dict[str, Any]:
        """
        Score certifications (0-25 points, stackable).

        Award points for ANY certification found. No penalty for missing certs.
        Points per cert are predefined and stackable, capped at 25.
        """
        result: Dict[str, Any] = {"score": 0.0, "detail": "", "max": 25, "items": []}

        if not manufacturer.certifications:
            result["detail"] = "No certifications found"
            return result

        total = 0.0
        items = []

        for cert in manufacturer.certifications:
            cert_lower = cert.lower().strip()

            # "Working towards" language
            if any(kw in cert_lower for kw in ["working towards", "in progress", "pending"]):
                pts = WORKING_TOWARDS_POINTS
                items.append(f"{cert} (+{pts})")
                total += pts
                continue

            # Look up in known certifications
            matched = False
            for known, pts in CERT_POINTS.items():
                if known in cert_lower or cert_lower in known:
                    items.append(f"{cert} (+{pts})")
                    total += pts
                    matched = True
                    break

            if not matched:
                if any(kw in cert_lower for kw in ["quality", "ethical", "standard", "compliant"]):
                    items.append(f"{cert} (+{MENTIONS_STANDARDS_POINTS})")
                    total += MENTIONS_STANDARDS_POINTS
                else:
                    items.append(f"{cert} (+{DEFAULT_CERT_POINTS})")
                    total += DEFAULT_CERT_POINTS

        result["score"] = min(25.0, total)
        result["items"] = items
        result["detail"] = ", ".join(items)
        return result

    # ------------------------------------------------------------------
    # 4. Materials Capability (0-15 points, stackable)
    # ------------------------------------------------------------------

    def _score_materials(
        self, manufacturer: Manufacturer, criteria: SearchCriteria
    ) -> Dict[str, Any]:
        """
        Score materials capability (0-15 points, stackable).

        - Each material matching user's request: 5 pts
        - Similar/alternative material: 3 pts
        - "Can source any material": 8 pts
        - Premium/technical materials: 5 pts
        - Sustainable materials: 4 pts
        - Cap at 15
        """
        result: Dict[str, Any] = {"score": 0.0, "detail": "", "max": 15, "items": []}

        if not manufacturer.materials:
            result["detail"] = "Materials unknown"
            return result

        mfr_lower = [m.lower() for m in manufacturer.materials]
        mfr_text = " ".join(mfr_lower)
        total = 0.0
        items = []

        # "Any material" / "custom materials"
        if any(kw in mfr_text for kw in ["any material", "custom material", "all materials", "any fabric"]):
            total += 8.0
            items.append("Custom/any materials (+8)")

        # Match against user criteria
        if criteria.materials:
            for crit_mat in criteria.materials:
                crit_lower = crit_mat.lower()
                # Direct match
                if any(crit_lower in m or m in crit_lower for m in mfr_lower):
                    total += 5.0
                    items.append(f"{crit_mat} (match, +5)")
                # Similarity match
                elif self._materials_related(crit_lower, mfr_lower):
                    total += 3.0
                    items.append(f"{crit_mat} (similar, +3)")

        # Sustainable materials bonus
        if any(kw in mfr_text for kw in SUSTAINABLE_MATERIAL_KEYWORDS):
            total += 4.0
            items.append("Sustainable materials (+4)")

        # Premium/technical materials bonus
        if any(kw in mfr_text for kw in PREMIUM_MATERIAL_KEYWORDS):
            total += 5.0
            items.append("Premium/technical materials (+5)")

        result["score"] = min(15.0, total)
        result["items"] = items
        result["detail"] = ", ".join(items) if items else "Materials listed, no criteria match"
        return result

    @staticmethod
    def _materials_related(target: str, mfr_materials: List[str]) -> bool:
        """Check if *target* is in the same material family as any manufacturer material."""
        for members in MATERIAL_FAMILIES.values():
            target_in = any(m in target or target in m for m in members)
            if target_in:
                for mfr_mat in mfr_materials:
                    if any(m in mfr_mat or mfr_mat in m for m in members):
                        return True
        return False

    # ------------------------------------------------------------------
    # 5. Production Methods (0-15 points, stackable)
    # ------------------------------------------------------------------

    def _score_production_methods(
        self, manufacturer: Manufacturer, criteria: SearchCriteria
    ) -> Dict[str, Any]:
        """
        Score production methods (0-15 points, stackable).

        - Each method matching user's request: 5 pts
        - Related/complementary method: 3 pts
        - "Full service manufacturing": 10 pts
        - Shows production facility details: 5 pts
        - Cap at 15
        """
        result: Dict[str, Any] = {"score": 0.0, "detail": "", "max": 15, "items": []}

        if not manufacturer.production_methods:
            result["detail"] = "Production methods unknown"
            return result

        mfr_lower = [m.lower() for m in manufacturer.production_methods]
        mfr_text = " ".join(mfr_lower)
        total = 0.0
        items = []

        # Full service manufacturing
        if any(kw in mfr_text for kw in FULL_SERVICE_KEYWORDS):
            total += 10.0
            items.append("Full service manufacturing (+10)")

        # Match against user criteria
        if criteria.production_methods:
            for crit_method in criteria.production_methods:
                crit_lower = crit_method.lower()
                if any(crit_lower in m or m in crit_lower for m in mfr_lower):
                    total += 5.0
                    items.append(f"{crit_method} (match, +5)")
                elif self._methods_related(crit_lower, mfr_lower):
                    total += 3.0
                    items.append(f"{crit_method} (related, +3)")

        # Facility detail bonus
        facility_kw = ["factory", "facility", "equipment", "machinery", "production line", "sqm", "sq ft"]
        if any(kw in mfr_text for kw in facility_kw):
            total += 5.0
            items.append("Facility details shown (+5)")

        result["score"] = min(15.0, total)
        result["items"] = items
        result["detail"] = ", ".join(items) if items else "Methods listed, no criteria match"
        return result

    @staticmethod
    def _methods_related(target: str, mfr_methods: List[str]) -> bool:
        """Check if *target* is in the same method family as any manufacturer method."""
        for members in METHOD_FAMILIES.values():
            target_in = any(m in target or target in m for m in members)
            if target_in:
                for mfr_method in mfr_methods:
                    if any(m in mfr_method or mfr_method in m for m in members):
                        return True
        return False

    # ------------------------------------------------------------------
    # Bonus Points (stackable, can push above 100 before final cap)
    # ------------------------------------------------------------------

    def _score_bonuses(self, manufacturer: Manufacturer) -> Dict[str, Any]:
        """
        Score bonus points based on available data signals.

        Website Quality & Transparency:
        - Professional, detailed website: +8
        - Clear contact information visible: +4
        - Multiple contact methods: +3
        - Modern/responsive website design: +2

        Credibility Signals (from website_signals dict if populated):
        - Testimonials/case studies: +5
        - Portfolio shown: +4
        - Factory photos: +4
        - Industry awards: +3
        - 10+ years in business: +3

        Sustainability & Ethics (from website_signals):
        - Strong sustainability messaging: +5
        - Transparent supply chain: +4
        - Social responsibility programs: +3
        - Environmental initiatives: +3

        Business Indicators (from website_signals):
        - Recent news/updates: +3
        - Export experience: +3
        - International clients: +2
        - Trade show participation: +2
        """
        result: Dict[str, Any] = {"score": 0.0, "detail": "", "items": []}
        total = 0.0
        items = []

        # --- Contact information signals ---
        contact_count = sum([
            bool(manufacturer.contact.email),
            bool(manufacturer.contact.phone),
            bool(manufacturer.contact.address),
        ])

        if contact_count >= 1:
            total += 4.0
            items.append("Contact info visible (+4)")
        if contact_count >= 2:
            total += 3.0
            items.append("Multiple contact methods (+3)")

        # --- Data richness as proxy for professional website ---
        populated = sum([
            bool(manufacturer.location),
            bool(manufacturer.materials),
            bool(manufacturer.production_methods),
            bool(manufacturer.certifications),
            manufacturer.moq is not None,
            bool(manufacturer.contact.email),
            bool(manufacturer.contact.phone),
            bool(manufacturer.contact.address),
        ])

        if populated >= 7:
            total += 8.0
            items.append("Professional, detailed website (+8)")
        elif populated >= 5:
            total += 6.0
            items.append("Good website detail (+6)")
        elif populated >= 3:
            total += 4.0
            items.append("Basic website detail (+4)")

        # --- website_signals (populated by DataExtractor when available) ---
        signals = manufacturer.website_signals
        if signals and isinstance(signals, dict):
            signal_map = [
                ("testimonials", 5, "Client testimonials (+5)"),
                ("portfolio", 4, "Portfolio shown (+4)"),
                ("factory_photos", 4, "Factory photos (+4)"),
                ("awards", 3, "Industry awards (+3)"),
                ("sustainability_focus", 5, "Strong sustainability messaging (+5)"),
                ("transparent_supply_chain", 4, "Transparent supply chain (+4)"),
                ("social_responsibility", 3, "Social responsibility programs (+3)"),
                ("environmental_initiatives", 3, "Environmental initiatives (+3)"),
                ("recent_updates", 3, "Recent news/updates (+3)"),
                ("export_experience", 3, "Export experience (+3)"),
                ("international_clients", 2, "International client base (+2)"),
                ("trade_shows", 2, "Trade show participation (+2)"),
            ]
            for key, pts, label in signal_map:
                if signals.get(key):
                    total += pts
                    items.append(label)

            yrs = signals.get("years_in_business")
            if yrs and isinstance(yrs, (int, float)) and yrs >= 10:
                total += 3.0
                items.append(f"{int(yrs)} years in business (+3)")

        result["score"] = total
        result["items"] = items
        result["detail"] = ", ".join(items) if items else "No bonus signals detected"
        return result

    # ------------------------------------------------------------------
    # Confidence Assessment
    # ------------------------------------------------------------------

    def _assess_confidence(self, manufacturer: Manufacturer) -> str:
        """
        Assess confidence based on data completeness, source quality, and verification.

        HIGH:   75%+ confidence score
        MEDIUM: 50-74%
        LOW:    <50%
        """
        completeness = self._completeness_pct(manufacturer)

        # Source quality multiplier
        src = (manufacturer.source_url or "").lower()
        if any(p in src for p in ["alibaba.com", "indiamart.com", "makersrow.com", "thomasnet.com"]):
            source_mult = 1.0  # B2B platform
        elif any(d in src for d in ["directory", "listing", "yellowpages"]):
            source_mult = 0.8  # Directory
        else:
            source_mult = 1.2  # Likely official website

        # Verification bonus
        verification_bonus = 0
        if manufacturer.website_signals and isinstance(manufacturer.website_signals, dict):
            if manufacturer.website_signals.get("multiple_sources"):
                verification_bonus += 10
            if manufacturer.website_signals.get("recent_updates"):
                verification_bonus += 5

        confidence_score = (completeness * source_mult) + verification_bonus

        if confidence_score >= 75:
            return "high"
        elif confidence_score >= 50:
            return "medium"
        else:
            return "low"

    # ------------------------------------------------------------------
    # Notes / Scoring Breakdown
    # ------------------------------------------------------------------

    def _generate_breakdown(
        self,
        manufacturer: Manufacturer,
        breakdown: Dict[str, Any],
        base_score: float,
        bonus_score: float,
        conflict_deduction: float,
        final_score: float,
    ) -> str:
        """Generate detailed scoring breakdown for the notes field."""
        lines = ["Scoring Breakdown:"]

        for label, key in [
            ("Location", "location"),
            ("MOQ", "moq"),
            ("Certifications", "certifications"),
            ("Materials", "materials"),
            ("Production", "production"),
        ]:
            cat = breakdown[key]
            prefix = "\u2713" if cat["score"] > 0 else "\u25CB"
            if cat.get("items"):
                detail = ", ".join(cat["items"])
            else:
                detail = cat["detail"]
            lines.append(f"{prefix} {label}: {detail} = +{cat['score']:.0f} pts")

        bonuses = breakdown["bonuses"]
        if bonuses["score"] > 0:
            detail = ", ".join(bonuses["items"])
            lines.append(f"\u2713 Bonuses: {detail} = +{bonuses['score']:.0f} pts")

        lines.append("")
        lines.append(f"Subtotal: {base_score:.0f} points")
        if bonus_score > 0:
            after = base_score + bonus_score
            cap_note = " (capped at 100)" if after > 100 else ""
            lines.append(f"After bonuses: {after:.0f} points{cap_note}")
        if conflict_deduction > 0:
            lines.append(f"Conflict deduction: -{conflict_deduction:.0f} pts")
        lines.append(f"Final Score: {final_score:.0f}")

        comp = self._completeness_pct(manufacturer)
        lines.append(
            f"Confidence: {manufacturer.confidence.title()} "
            f"({comp:.0f}% data complete)"
        )

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _completeness_pct(manufacturer: Manufacturer) -> float:
        """Percentage of key data fields that are populated."""
        total = 8
        filled = sum([
            bool(manufacturer.location),
            bool(manufacturer.contact.email),
            bool(manufacturer.contact.phone),
            bool(manufacturer.materials),
            bool(manufacturer.production_methods),
            manufacturer.moq is not None,
            bool(manufacturer.certifications),
            bool(manufacturer.contact.address),
        ])
        return (filled / total) * 100
