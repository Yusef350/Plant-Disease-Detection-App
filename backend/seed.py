"""
Database seed script — populates diseases and plants collections.
Run once: python seed.py
"""

import sys
import os

# Allow imports from the backend directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.db import get_db, init_db

# ── Plant data ───────────────────────────────────────────────────────────

PLANTS = [
    {"commonName": "Apple", "scientificName": "Malus domestica"},
    {"commonName": "Blueberry", "scientificName": "Vaccinium corymbosum"},
    {"commonName": "Cherry (including sour)", "scientificName": "Prunus cerasus"},
    {"commonName": "Corn (maize)", "scientificName": "Zea mays"},
    {"commonName": "Grape", "scientificName": "Vitis vinifera"},
    {"commonName": "Orange", "scientificName": "Citrus sinensis"},
    {"commonName": "Peach", "scientificName": "Prunus persica"},
    {"commonName": "Pepper, bell", "scientificName": "Capsicum annuum"},
    {"commonName": "Potato", "scientificName": "Solanum tuberosum"},
    {"commonName": "Raspberry", "scientificName": "Rubus idaeus"},
    {"commonName": "Soybean", "scientificName": "Glycine max"},
    {"commonName": "Squash", "scientificName": "Cucurbita spp."},
    {"commonName": "Strawberry", "scientificName": "Fragaria × ananassa"},
    {"commonName": "Tomato", "scientificName": "Solanum lycopersicum"},
]

# ── Disease data (all 38 classes) ────────────────────────────────────────

DISEASES = [
    {
        "name": "Apple___Apple_scab",
        "description": "Apple scab is a common fungal disease caused by Venturia inaequalis that affects apple trees worldwide.",
        "symptoms": "Olive-green to dark brown lesions on leaves, fruit, and sometimes twigs. Leaves may curl and drop early.",
        "causes": "Fungus Venturia inaequalis; spreads via wind-blown spores in cool, wet spring weather.",
        "treatment": "Apply fungicides (captan, myclobutanil) starting at green tip stage. Remove fallen leaves. Prune for air circulation.",
        "prevention": "Plant scab-resistant varieties. Clean up fallen leaves in autumn. Ensure good air circulation through pruning.",
        "severity": "medium",
    },
    {
        "name": "Apple___Black_rot",
        "description": "Black rot is a fungal disease caused by Botryosphaeria obtusa that affects apple fruit, leaves, and bark.",
        "symptoms": "Brown, expanding lesions on leaves; black, rotting areas on fruit starting at the blossom end; cankers on limbs.",
        "causes": "Fungus Botryosphaeria obtusa; overwinters in mummified fruit and dead bark.",
        "treatment": "Remove mummified fruit and cankers. Apply captan or thiophanate-methyl fungicides during the growing season.",
        "prevention": "Prune dead wood annually. Remove mummified fruit from trees and ground. Maintain tree vigor with proper fertilization.",
        "severity": "high",
    },
    {
        "name": "Apple___Cedar_apple_rust",
        "description": "Cedar apple rust is caused by the fungus Gymnosporangium juniperi-virginianae, which requires both cedar and apple host trees.",
        "symptoms": "Bright orange-yellow spots on upper leaf surface; tube-like structures on the underside of leaves.",
        "causes": "Fungus Gymnosporangium juniperi-virginianae; requires juniper/cedar and apple as alternate hosts.",
        "treatment": "Apply fungicides (myclobutanil, triadimefon) from pink bud through petal fall. Remove nearby cedar/juniper trees if possible.",
        "prevention": "Plant resistant apple varieties. Remove juniper and cedar trees within a few hundred metres of apple orchards.",
        "severity": "medium",
    },
    {
        "name": "Apple___healthy",
        "description": "The apple plant is healthy with no signs of disease.",
        "symptoms": "No disease symptoms present.",
        "causes": "",
        "treatment": "No treatment needed. Continue regular maintenance.",
        "prevention": "Maintain good agricultural practices, proper watering, and balanced fertilization.",
        "severity": "low",
    },
    {
        "name": "Blueberry___healthy",
        "description": "The blueberry plant is healthy with no signs of disease.",
        "symptoms": "No disease symptoms present.",
        "causes": "",
        "treatment": "No treatment needed. Continue regular maintenance.",
        "prevention": "Ensure acidic soil pH (4.5–5.5), proper mulching, and adequate irrigation.",
        "severity": "low",
    },
    {
        "name": "Cherry_(including_sour)___Powdery_mildew",
        "description": "Powdery mildew on cherry is caused by Podosphaera clandestina, forming a white powdery coating on leaves.",
        "symptoms": "White powdery patches on leaves, shoots, and sometimes fruit. Leaves may curl, become distorted, and drop prematurely.",
        "causes": "Fungus Podosphaera clandestina; favoured by warm, dry days and cool nights with high humidity.",
        "treatment": "Apply sulfur-based or triazole fungicides. Remove and destroy infected shoots. Improve air circulation.",
        "prevention": "Plant resistant varieties. Avoid overhead irrigation. Prune to improve airflow. Apply preventive fungicides before symptoms appear.",
        "severity": "medium",
    },
    {
        "name": "Cherry_(including_sour)___healthy",
        "description": "The cherry plant is healthy with no signs of disease.",
        "symptoms": "No disease symptoms present.",
        "causes": "",
        "treatment": "No treatment needed.",
        "prevention": "Proper pruning, good drainage, and balanced nutrition.",
        "severity": "low",
    },
    {
        "name": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
        "description": "Gray leaf spot is a foliar disease of corn caused by Cercospora zeae-maydis, leading to significant yield losses.",
        "symptoms": "Rectangular, grey to tan lesions running parallel to leaf veins. Lesions may merge and cause large areas of dead tissue.",
        "causes": "Fungus Cercospora zeae-maydis; survives in crop debris and is favoured by warm, humid conditions.",
        "treatment": "Apply foliar fungicides (strobilurins, triazoles) at VT to R1 growth stages. Rotate with non-host crops.",
        "prevention": "Use resistant hybrids. Rotate crops. Tillage to bury infected residue. Avoid continuous corn planting.",
        "severity": "high",
    },
    {
        "name": "Corn_(maize)___Common_rust_",
        "description": "Common rust of corn is caused by Puccinia sorghi, producing small reddish-brown pustules on leaves.",
        "symptoms": "Small, circular to elongated, reddish-brown pustules on both leaf surfaces. Severe infections can reduce photosynthesis.",
        "causes": "Fungus Puccinia sorghi; spores are wind-borne and favour moderate temperatures (16–23°C) with high humidity.",
        "treatment": "Apply foliar fungicides if infection occurs before tasseling. Most modern hybrids have adequate resistance.",
        "prevention": "Plant resistant hybrids. Early planting can help plants mature before peak spore periods.",
        "severity": "medium",
    },
    {
        "name": "Corn_(maize)___Northern_Leaf_Blight",
        "description": "Northern corn leaf blight (NCLB) is caused by Exserohilum turcicum, causing large cigar-shaped lesions on corn leaves.",
        "symptoms": "Long (2–15 cm), elliptical, greyish-green to tan lesions on leaves. Lesions may coalesce and kill entire leaves.",
        "causes": "Fungus Exserohilum turcicum; overwinters in corn debris and is favoured by moderate temperatures and wet weather.",
        "treatment": "Apply foliar fungicides at tasseling stage if disease pressure is high. Use resistant hybrids.",
        "prevention": "Plant resistant hybrids. Rotate with non-host crops. Till to bury crop debris.",
        "severity": "high",
    },
    {
        "name": "Corn_(maize)___healthy",
        "description": "The corn plant is healthy with no signs of disease.",
        "symptoms": "No disease symptoms present.",
        "causes": "",
        "treatment": "No treatment needed.",
        "prevention": "Follow recommended planting practices, ensure adequate nutrition and water management.",
        "severity": "low",
    },
    {
        "name": "Grape___Black_rot",
        "description": "Grape black rot is caused by the fungus Guignardia bidwellii, resulting in fruit and leaf damage.",
        "symptoms": "Brown circular lesions on leaves; black, shriveled mummified fruit; dark lesions on shoots.",
        "causes": "Fungus Guignardia bidwellii; overwinters in mummified berries and infected canes.",
        "treatment": "Apply fungicides (myclobutanil, mancozeb) from bud break through veraison. Remove mummified fruit.",
        "prevention": "Remove all mummies from vines and ground. Prune for good air circulation. Use resistant varieties when possible.",
        "severity": "high",
    },
    {
        "name": "Grape___Esca_(Black_Measles)",
        "description": "Esca (black measles) is a complex trunk disease of grapevines caused by several fungal species.",
        "symptoms": "Tiger-stripe pattern on leaves; dark spots on berries; sometimes sudden vine collapse (apoplexy).",
        "causes": "Multiple fungi including Phaeomoniella chlamydospora and Phaeoacremonium spp.; enter through pruning wounds.",
        "treatment": "No fully effective treatment. Remedial surgery (cutting out trunk cankers). Apply pruning wound protectants.",
        "prevention": "Protect pruning wounds with fungicidal paste. Delay pruning to late winter. Avoid large pruning wounds.",
        "severity": "high",
    },
    {
        "name": "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
        "description": "Leaf blight of grapes is caused by Pseudocercospora vitis (formerly Isariopsis), creating angular leaf spots.",
        "symptoms": "Dark brown, angular spots on leaves bounded by veins. Severe infections can cause defoliation.",
        "causes": "Fungus Pseudocercospora vitis; favoured by warm, humid conditions and dense canopies.",
        "treatment": "Apply copper-based or mancozeb fungicides. Remove infected leaves. Improve canopy airflow.",
        "prevention": "Open canopy through pruning. Avoid overhead irrigation. Maintain sanitation by removing fallen leaves.",
        "severity": "medium",
    },
    {
        "name": "Grape___healthy",
        "description": "The grape plant is healthy with no signs of disease.",
        "symptoms": "No disease symptoms present.",
        "causes": "",
        "treatment": "No treatment needed.",
        "prevention": "Proper trellising, balanced fertilization, and good pest management.",
        "severity": "low",
    },
    {
        "name": "Orange___Haunglongbing_(Citrus_greening)",
        "description": "Huanglongbing (HLB) or citrus greening is one of the most devastating citrus diseases worldwide, caused by bacteria.",
        "symptoms": "Asymmetric blotchy mottle on leaves; small, lopsided, bitter fruit that stays green; yellow shoots.",
        "causes": "Bacterium Candidatus Liberibacter spp.; transmitted by the Asian citrus psyllid (Diaphorina citri).",
        "treatment": "No cure exists. Remove infected trees. Control psyllid vectors with insecticides. Nutritional therapies may help symptom management.",
        "prevention": "Control psyllid populations aggressively. Use certified disease-free nursery stock. Monitor regularly and remove infected trees promptly.",
        "severity": "high",
    },
    {
        "name": "Peach___Bacterial_spot",
        "description": "Bacterial spot of peach is caused by Xanthomonas arboricola pv. pruni, affecting leaves, fruit, and twigs.",
        "symptoms": "Small, angular, water-soaked spots on leaves that turn dark; lesions crack and cause shot-hole appearance; fruit lesions.",
        "causes": "Bacterium Xanthomonas arboricola pv. pruni; spread by rain splash and wind-driven rain.",
        "treatment": "Apply copper sprays at leaf fall and early spring. Oxytetracycline sprays during growing season in severe cases.",
        "prevention": "Plant resistant varieties. Avoid overhead irrigation. Maintain proper tree spacing for air circulation.",
        "severity": "medium",
    },
    {
        "name": "Peach___healthy",
        "description": "The peach plant is healthy with no signs of disease.",
        "symptoms": "No disease symptoms present.",
        "causes": "",
        "treatment": "No treatment needed.",
        "prevention": "Proper pruning, adequate drainage, and balanced fertilization.",
        "severity": "low",
    },
    {
        "name": "Pepper,_bell___Bacterial_spot",
        "description": "Bacterial spot of pepper is caused by Xanthomonas spp., leading to leaf spots and fruit lesions.",
        "symptoms": "Small, water-soaked spots on leaves that become brown and papery; raised scab-like spots on fruit.",
        "causes": "Xanthomonas campestris pv. vesicatoria and related species; seed-borne and spread by rain splash.",
        "treatment": "Apply copper-based bactericides. Remove and destroy infected plants. No fully effective chemical control.",
        "prevention": "Use certified disease-free seed. Rotate crops (2–3 year rotation). Avoid overhead irrigation.",
        "severity": "medium",
    },
    {
        "name": "Pepper,_bell___healthy",
        "description": "The bell pepper plant is healthy with no signs of disease.",
        "symptoms": "No disease symptoms present.",
        "causes": "",
        "treatment": "No treatment needed.",
        "prevention": "Proper spacing, adequate nutrition, and good water management.",
        "severity": "low",
    },
    {
        "name": "Potato___Early_blight",
        "description": "Early blight of potato is caused by Alternaria solani, one of the most common potato diseases worldwide.",
        "symptoms": "Dark brown, concentric-ringed (target-shaped) lesions on lower leaves first; stems may also develop lesions.",
        "causes": "Fungus Alternaria solani; overwinters in crop debris and soil. Favoured by warm temperatures and wet foliage.",
        "treatment": "Apply fungicides (chlorothalonil, mancozeb, azoxystrobin) on a 7–10 day schedule when conditions favour disease.",
        "prevention": "Use resistant varieties. Destroy crop debris. Rotate with non-solanaceous crops. Avoid overhead irrigation.",
        "severity": "medium",
    },
    {
        "name": "Potato___Late_blight",
        "description": "Late blight is caused by the oomycete Phytophthora infestans — the same pathogen responsible for the Irish Potato Famine.",
        "symptoms": "Water-soaked greyish-green spots on leaves that rapidly enlarge; white mold on leaf undersides; tuber rot.",
        "causes": "Oomycete Phytophthora infestans; spreads rapidly under cool (10–24°C), wet conditions via airborne sporangia.",
        "treatment": "Apply protectant fungicides (chlorothalonil, mancozeb) or systemic fungicides (metalaxyl). Remove infected plants immediately.",
        "prevention": "Plant certified disease-free seed tubers. Destroy volunteer potatoes. Use resistant varieties. Hill tubers properly.",
        "severity": "high",
    },
    {
        "name": "Potato___healthy",
        "description": "The potato plant is healthy with no signs of disease.",
        "symptoms": "No disease symptoms present.",
        "causes": "",
        "treatment": "No treatment needed.",
        "prevention": "Proper hilling, crop rotation, and certified seed use.",
        "severity": "low",
    },
    {
        "name": "Raspberry___healthy",
        "description": "The raspberry plant is healthy with no signs of disease.",
        "symptoms": "No disease symptoms present.",
        "causes": "",
        "treatment": "No treatment needed.",
        "prevention": "Proper pruning of spent canes, good drainage, and adequate spacing.",
        "severity": "low",
    },
    {
        "name": "Soybean___healthy",
        "description": "The soybean plant is healthy with no signs of disease.",
        "symptoms": "No disease symptoms present.",
        "causes": "",
        "treatment": "No treatment needed.",
        "prevention": "Proper crop rotation, balanced nutrition, and good seed quality.",
        "severity": "low",
    },
    {
        "name": "Squash___Powdery_mildew",
        "description": "Powdery mildew on squash is caused by Podosphaera xanthii and Erysiphe cichoracearum fungi.",
        "symptoms": "White, powdery fungal growth on upper and lower leaf surfaces; leaves turn yellow and die; reduced fruit quality.",
        "causes": "Fungi Podosphaera xanthii or Erysiphe cichoracearum; favoured by warm, dry days and cool, humid nights.",
        "treatment": "Apply sulfur, potassium bicarbonate, or triazole fungicides. Neem oil can help in early stages.",
        "prevention": "Plant resistant varieties. Ensure good air circulation. Avoid excessive nitrogen fertilization.",
        "severity": "medium",
    },
    {
        "name": "Strawberry___Leaf_scorch",
        "description": "Leaf scorch of strawberry is caused by the fungus Diplocarpon earlianum, affecting leaf tissue.",
        "symptoms": "Small, dark purple spots on upper leaf surface; spots enlarge and margins appear scorched; premature leaf death.",
        "causes": "Fungus Diplocarpon earlianum; overwinters in infected leaves and spreads by rain splash.",
        "treatment": "Apply fungicides (captan, thiram) starting at bloom. Remove and destroy infected leaves.",
        "prevention": "Plant resistant varieties. Renovate beds after harvest. Ensure good air circulation. Remove old leaves.",
        "severity": "medium",
    },
    {
        "name": "Strawberry___healthy",
        "description": "The strawberry plant is healthy with no signs of disease.",
        "symptoms": "No disease symptoms present.",
        "causes": "",
        "treatment": "No treatment needed.",
        "prevention": "Good site preparation, raised beds, proper spacing, and mulching.",
        "severity": "low",
    },
    {
        "name": "Tomato___Bacterial_spot",
        "description": "Bacterial spot of tomato is caused by several Xanthomonas species, affecting leaves, stems, and fruit.",
        "symptoms": "Small, dark, water-soaked spots on leaves; spots may have yellow halos; raised, scabby lesions on fruit.",
        "causes": "Xanthomonas spp.; seed-borne and spread by rain splash, overhead irrigation, and contaminated tools.",
        "treatment": "Copper-based bactericides provide partial control. Remove severely infected plants.",
        "prevention": "Use disease-free seed and transplants. Rotate crops. Avoid overhead irrigation. Sanitize tools.",
        "severity": "medium",
    },
    {
        "name": "Tomato___Early_blight",
        "description": "Early blight of tomato is caused by Alternaria solani, one of the most common tomato diseases.",
        "symptoms": "Dark brown spots with concentric rings (target-like) on lower leaves first; stem lesions; leathery fruit rot at stem end.",
        "causes": "Fungus Alternaria solani; survives in crop debris and soil; favoured by warm, humid weather.",
        "treatment": "Apply fungicides (chlorothalonil, copper, mancozeb) on a regular schedule. Remove affected lower leaves.",
        "prevention": "Rotate crops (3-year cycle). Stake and mulch plants. Avoid overhead watering. Use resistant varieties.",
        "severity": "medium",
    },
    {
        "name": "Tomato___Late_blight",
        "description": "Late blight of tomato is caused by Phytophthora infestans and can destroy entire fields within days.",
        "symptoms": "Large, irregular, water-soaked greyish-green spots on leaves; white fuzzy growth on leaf undersides; firm, dark fruit rot.",
        "causes": "Oomycete Phytophthora infestans; thrives in cool (10–24°C), wet conditions; spreads rapidly via wind-borne spores.",
        "treatment": "Apply fungicides immediately (chlorothalonil, copper, mancozeb). Remove and destroy all infected plant material.",
        "prevention": "Use resistant varieties. Avoid overhead irrigation. Provide good air circulation. Monitor weather alerts for blight risk.",
        "severity": "high",
    },
    {
        "name": "Tomato___Leaf_Mold",
        "description": "Tomato leaf mold is caused by the fungus Passalora fulva (formerly Cladosporium fulvum) and mainly occurs in greenhouses.",
        "symptoms": "Pale greenish-yellow spots on upper leaf surface; olive-green to greyish-purple velvety mold on lower surface.",
        "causes": "Fungus Passalora fulva; favoured by high humidity (>85%) and moderate temperatures in enclosed environments.",
        "treatment": "Improve ventilation and reduce humidity. Apply fungicides (chlorothalonil, copper). Remove infected leaves.",
        "prevention": "Ensure good greenhouse ventilation. Avoid leaf wetness. Use resistant varieties. Space plants adequately.",
        "severity": "medium",
    },
    {
        "name": "Tomato___Septoria_leaf_spot",
        "description": "Septoria leaf spot is caused by Septoria lycopersici and is one of the most destructive tomato foliar diseases.",
        "symptoms": "Numerous small, circular spots (1–3 mm) with dark borders and grey centres with tiny black dots (pycnidia).",
        "causes": "Fungus Septoria lycopersici; survives on crop debris and solanaceous weeds; spread by rain splash.",
        "treatment": "Apply fungicides (chlorothalonil, mancozeb, copper) starting when first symptoms appear. Remove lower infected leaves.",
        "prevention": "Rotate crops. Eliminate solanaceous weeds. Mulch around plants. Avoid overhead irrigation. Stake plants.",
        "severity": "medium",
    },
    {
        "name": "Tomato___Spider_mites Two-spotted_spider_mite",
        "description": "Two-spotted spider mite (Tetranychus urticae) is a common pest of tomato that causes leaf stippling and defoliation.",
        "symptoms": "Fine stippling (tiny yellow/white dots) on leaf surfaces; webbing on undersides of leaves; leaf browning and drop.",
        "causes": "Tetranychus urticae mites; thrive in hot, dry conditions; populations can explode rapidly.",
        "treatment": "Apply miticides (abamectin, bifenthrin) or insecticidal soap/horticultural oil. Introduce predatory mites (Phytoseiulus persimilis).",
        "prevention": "Maintain adequate irrigation (mites prefer drought-stressed plants). Avoid broad-spectrum insecticides that kill beneficial predators.",
        "severity": "medium",
    },
    {
        "name": "Tomato___Target_Spot",
        "description": "Target spot of tomato is caused by Corynespora cassiicola, producing concentric-ringed lesions on leaves and fruit.",
        "symptoms": "Small, brown spots with concentric rings on leaves and fruit; lesions may coalesce; premature defoliation.",
        "causes": "Fungus Corynespora cassiicola; favoured by warm, wet conditions; survives in crop debris.",
        "treatment": "Apply fungicides (chlorothalonil, azoxystrobin). Remove severely infected leaves. Rotate with non-host crops.",
        "prevention": "Crop rotation. Good sanitation. Adequate plant spacing. Avoid overhead irrigation.",
        "severity": "medium",
    },
    {
        "name": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        "description": "Tomato yellow leaf curl virus (TYLCV) is a devastating viral disease transmitted by whiteflies.",
        "symptoms": "Severe upward curling and yellowing of leaves; stunted growth; reduced fruit set; small, pale fruit.",
        "causes": "Begomovirus (TYLCV); transmitted by silverleaf whitefly (Bemisia tabaci) in a persistent manner.",
        "treatment": "No cure for infected plants — remove and destroy them. Control whitefly populations with insecticides or sticky traps.",
        "prevention": "Use TYLCV-resistant varieties. Control whiteflies early. Use reflective mulches to repel whiteflies. Use insect-proof netting.",
        "severity": "high",
    },
    {
        "name": "Tomato___Tomato_mosaic_virus",
        "description": "Tomato mosaic virus (ToMV) is a highly stable and contagious plant virus that affects tomato production.",
        "symptoms": "Light and dark green mosaic pattern on leaves; leaf distortion and fern-like appearance; reduced or mottled fruit.",
        "causes": "Tobamovirus ToMV; extremely stable and spread by contaminated tools, hands, seed, and soil.",
        "treatment": "No chemical treatment. Remove infected plants immediately. Sanitize all tools with 10% bleach or milk solution.",
        "prevention": "Use resistant varieties (Tm-2 gene). Sanitize seed with dry heat (70°C, 2–4 days). Wash hands before handling plants.",
        "severity": "high",
    },
    {
        "name": "Tomato___healthy",
        "description": "The tomato plant is healthy with no signs of disease.",
        "symptoms": "No disease symptoms present.",
        "causes": "",
        "treatment": "No treatment needed.",
        "prevention": "Proper staking, mulching, balanced fertilization, and consistent watering.",
        "severity": "low",
    },
]


def seed():
    """Seed the database with plants and diseases."""
    db = get_db()

    # Initialize indexes
    init_db()

    # ── Seed plants ──────────────────────────────────────────────────
    print("Seeding plants...")
    plants_inserted = 0
    for p in PLANTS:
        if not db.plants.find_one({"commonName": p["commonName"]}):
            db.plants.insert_one(p)
            plants_inserted += 1
    print(f"  → {plants_inserted} new plants inserted ({len(PLANTS)} total)")

    # ── Seed diseases ────────────────────────────────────────────────
    print("Seeding diseases...")
    diseases_inserted = 0
    for d in DISEASES:
        if not db.diseases.find_one({"name": d["name"]}):
            db.diseases.insert_one(d)
            diseases_inserted += 1
    print(f"  → {diseases_inserted} new diseases inserted ({len(DISEASES)} total)")

    print("\n✅ Seed complete!")


if __name__ == "__main__":
    seed()
