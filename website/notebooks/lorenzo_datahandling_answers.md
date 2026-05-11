## 1. Basic stats

### Data cleaning and preprocessing choices

Our six source datasets were downloaded directly from NYC Open Data via their Socrata API. Each went through a shared cleaning pipeline before use.

**Coordinate extraction and validation.** Several datasets (drinking fountains, public toilets) store geometry as WKT strings in the format `POINT (longitude latitude)` — note the reversed order, which is a common WGS84 pitfall. We parsed these with a regex extractor and swapped the values into explicit `latitude` and `longitude` columns. For datasets that already provided separate coordinate columns (drop-in centers, LinkNYC, drug crime), we coerced them to numeric and dropped rows where conversion failed.

After extraction we applied a spatial bounding box filter (latitude 40.0–42.0, longitude −75.0 to −72.0) to remove the null island at (0, 0) and any stray out-of-state points that passed numeric coercion. This was necessary because several rows had placeholder values rather than true missing data.

**Borough standardization.** Borough labels appeared in at least five different formats across the datasets — single letters (`M`, `B`, `X`, `Q`, `R`), two-letter codes (`MN`, `BK`, `BX`, `QN`, `SI`), mixed-case strings, and full names. We built a lookup map to normalize all of these to the five canonical full names so datasets could be joined or compared on a common key.

**Temporal filtering.** The drug crime dataset spans many years. We restricted it to incidents from 2014 onward to focus on the last decade and reduce the influence of outdated hotspot patterns on the survival score.

**Datasets with no spatial cleaning needed.** `shelter_repair` and `rhy_census` were loaded and saved as-is, since they were used for context rather than spatial scoring.

---

### Dataset statistics and exploratory findings

After cleaning, the dataset sizes are as follows:

| Dataset | Cleaned rows |
|---|---|
| Drinking fountains | ~1,600 |
| Public toilets | ~560 |
| Drop-in centers | ~70 |
| LinkNYC kiosks | ~2,000 |
| Drug crime (2014–) | ~60,000+ |

**Resource distribution is highly uneven across boroughs.** The grouped bar chart (log scale) shows that Manhattan and Brooklyn hold the large majority of most resource types. Staten Island consistently has the fewest resources across every category. The log scale was necessary because LinkNYC kiosk counts dwarf toilet and drop-in center counts by one to two orders of magnitude — a linear axis would have compressed the smaller datasets to near-zero bars.

**Crime incidents form clear geographic hotspots.** Rather than treating all crime points equally, we computed incident density per coordinate pair and retained only the top 5% of locations (the 95th percentile by count) for the heatmap layer. This highlights true hotspots rather than showing every single incident as uniform noise.

**Key imbalance to note.** Drop-in centers are the smallest dataset (~70 records) but receive the highest weight in the scoring formula. This means their geographic distribution has an outsized effect on the final survival scores — areas that happen to be near one of the few centers score substantially higher.

## 2. Data analysis

### Approach

Rather than train a supervised model — which would require labeled ground-truth "survivability" data that does not exist for this problem — we engineered a composite index that combines proximity to resources and exposure to crime. The goal was to produce a relative ranking of locations across NYC that could drive an interactive visualization.

**Scoring formula.** For each candidate point on the evaluation grid, we count the number of each resource type within approximately 1 km (±0.01 decimal degrees, roughly 1.1 km at NYC's latitude). These counts are combined into a weighted resource score:

```
resource_score = (fountains × 6) + (toilets × 10) + (LinkNYC × 4) + (centers × 15)
```

A risk penalty is then subtracted based on nearby crime density:

```
score = clip((resource_score − crime_count × 0.03) × 1.5, 0, 100)
```

The weights reflect relative utility for day-to-day survival needs: drop-in centers (15) offer the broadest support — shelter, meals, services — while toilets (10) and fountains (6) address basic sanitation and hydration. LinkNYC kiosks (4) are the most abundant and thus least scarce, so they contribute less per unit. These weights are heuristic and represent a deliberate design choice; they are tunable through the website's planned interactive weighting UI.

### What we learned

**Resource access and crime risk often co-occur in the same neighborhoods.** Mapping both layers together revealed that some of the highest-crime hotspots also have above-average resource density — particularly in parts of Manhattan. This means a raw resource count overstates survivability in those areas; the crime penalty corrects for this.

**Staten Island is the most resource-deprived borough by every measure.** It has the fewest fountains, toilets, LinkNYC kiosks, and drop-in centers in absolute terms, and its geographic isolation means that a single missing resource type can drop its survival scores substantially.

**The 1 km proximity radius is a meaningful choice.** At ±0.01 degrees, we are asking "what can a person reach on foot in roughly 10–15 minutes?" This is appropriate for a survival context but will undercount resources for people with access to transit. A network-distance approach would give more realistic accessibility estimates.