### Data cleaning and preprocessing choices
- **Coordinate extraction:** Extracted lat/lon from WKT `POINT (longitude latitude)` strings using regex, fixing the reversed WGS84 order.
- **Spatial filtering:** Applied a NYC bounding box (Lat 40.0–42.0, Lon -75.0 to -72.0) to drop missing/outlier coordinates (like 0,0).
- **Borough standardization:** Built a `BORO_MAP` to unify various naming formats (e.g., `M`, `MN`, `Manhattan`) across datasets.
- **Temporal filtering:** Restricted drug crime data to incidents from 2014 onward to ensure relevance.

---

### Dataset statistics and exploratory findings

| Dataset | Cleaned rows |
|---|---|
| Drinking fountains | ~1,600 |
| Public toilets | ~560 |
| Drop-in centers | ~70 |
| LinkNYC kiosks | ~2,000 |
| Drug crime (2014–) | ~60,000+ |

- **Uneven distribution:** Manhattan and Brooklyn dominate most resources, while Staten Island has the fewest. 
- **Crime hotspots:** We mapped only the 95th percentile of crime density, highlighting true danger zones over uniform noise.
- **Weight imbalances:** Drop-in centers (~70 records) have the highest impact on the score, meaning their scarce presence heavily skews local survivability.

## 2. Data analysis

### Approach
We engineered a composite "Survival Score" rather than training a supervised ML model, due to the lack of labeled ground-truth data. 

**Scoring formula (within a 1km radius / ±0.01 degrees):**
`resource_score = (fountains × 6) + (toilets × 10) + (LinkNYC × 4) + (centers × 15)`

**Risk Penalty:**
`score = clip((resource_score − crime_count × 0.03) × 1.5, 0, 100)`

These heuristic weights reflect daily survival utility: drop-in centers (15) provide comprehensive aid, while LinkNYC kiosks (4) are abundant but offer lower essential utility. 

### What we learned
- **Resource/Crime overlap:** High-resource areas (especially in Manhattan) frequently overlap with severe crime hotspots. The risk penalty successfully corrects inflated raw resource scores.
- **Staten Island deprivation:** The borough is isolated and consistently lacks basic survival resources across all categories.
- **Proximity context:** The 1km search radius accurately reflects a 10–15 minute walk, though it undercounts resources for those with transit access.