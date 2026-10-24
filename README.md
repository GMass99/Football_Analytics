# Football Analytics

Football (and some cricket) data analysis in Python: scraping public data, building metrics and models, and turning the results into visualisations. Many of the graphics were shared on Twitter at [@george__massey](https://twitter.com/george__massey).

## MSc dissertation

**Using Machine Learning to Predict Football Matches, Applied to the 2024/25 Premier League Season**
MSc Data Analytics, Queen Mary University of London (2024)

I built and compared machine learning models that predict how many goals each team scores in a match, then used them to simulate whole seasons. The models were trained on Premier League matches from 2017 to 2023, tested on 2023/24, and the selected model forecast the 2024/25 season.

- Poisson regression and multinomial logistic regression, tuned with grid search
- Model selection with repeated k-fold cross-validation, and bootstrap feature analysis
- Monte Carlo simulation of every fixture to give finishing-position probabilities

📄 [Read the dissertation (PDF)](Dissertation/George%20Massey%20-%20MSc%20Dissertation.pdf)

**Code** (in `Dissertation/Notebooks`, in the order they run):

1. **Scraping**: match data, market values and league position history
2. **Building the dataset**: previous-season data and league weights (1), average positions and general form (2), merging and removing duplicates (3), home and away form (4), market values (5), final clean before modelling (6)
3. **Goal distribution analysis**: checking goals against a Poisson distribution
4. **Models**: multiple Poisson regression and multiple logistic regression, each with tuning, evaluation and season simulation

## What's in this repository

| Folder | Contents |
|---|---|
| `Dissertation/` | The MSc dissertation and its notebooks |
| `Notebooks/` | Jupyter notebooks for each analysis, with outputs saved so charts show without running anything |
| `Data/` | The datasets the notebooks use |
| `Visuals/` | The finished graphics |

### Notebooks by theme

**Scraping and data collection**: match, shot, league and player data from FotMob, FBref, Understat, Transfermarkt and SofaScore, plus an introduction to StatsBomb open data.

**Metrics and modelling**
- Finishing skill vs luck: goals against xG and xGOT, for shooters and goalkeepers
- Rolling and moving-average xG, xGA and xGD form
- Linear and polynomial regression of league position and points on goal difference
- Player dependence, and team results with and without a player
- Wages against points and xGD

**Visualisation techniques**: pizza plots and radars for player and team profiles, shot maps, pass maps and pass networks, xG flow charts, beeswarms, bump charts, Voronoi diagrams and convex hulls, zones of control, and expected threat (xT).

**Case studies**: Norwich City (centre-back pairings, player positions, the impact of individual players), Championship and Premier League season reviews, and player comparisons.

**Cricket**: batting average against strike rate, and bowling strike rate against economy.

## Tools

Python, pandas, NumPy, scikit-learn, matplotlib, seaborn, mplsoccer, BeautifulSoup and requests.
