#  Movie Data Analysis Project

## Project Overview
This project analyzes a curated selection of popular movies using data from The Movie Database (TMDb) API. The analysis focuses on financial performance, audience reception, and comparative metrics between franchise and standalone films.

---
## Project Structure

    project/
    │── src/
    │   ├── extract.py
    │   └── transform.py
    │── movie_analysis.ipynb
    │── README.md
    │── requirements.txt

##  Approach & Methodology

### **1. Data Collection Strategy**
- **Targeted Movie Selection**: Pre-defined list of 19 movie IDs (including major franchise films and standalone hits)
- **API Integration**: Utilized TMDb API with secure API key management via `.env` file
- **Comprehensive Data Fetching**: Each API call includes `credits` append_to_response for cast/crew details
- **Error Handling**: Skip invalid IDs and log failed requests

### **2. Data Processing Pipeline**

#### **A. Initial Cleaning**
- Removed irrelevant columns (`adult`, `imdb_id`, `original_title`, `video`, `homepage`)
- Identified and processed JSON-like columns for extraction

#### **B. Structured Data Extraction**
- **Credits Processing**: Extracted director names, cast lists, and crew/cast sizes
- **Collection Handling**: Converted collection objects to franchise names
- **List Columns**: Flattened genres, languages, production companies/countries with pipe-separated format

#### **C. Data Type Standardization**
- Converted numeric columns (`budget`, `id`, `popularity`) to integers
- Parsed `release_date` to datetime format
- Created financial columns in millions USD with clear naming conventions

#### **D. Column Reorganization**
Logical grouping of columns for readability:
- Identification & Basic Info
- Financial Metrics
- Production Details
- Audience Metrics
- Crew/Cast Information

### **3. Key Performance Indicators (KPIs)**

#### **Financial Metrics**
- **Revenue Analysis**: Highest grossing movies
- **Budget Analysis**: Most expensive productions
- **Profit Calculation**: Revenue - Budget
- **ROI Analysis**: Return on Investment (with $10M+ budget filter)
- **Franchise vs Standalone**: Comparative financial performance

#### **Audience Metrics**
- **Voting Analysis**: Most voted and highest/lowest rated films
- **Popularity Scores**: TMDb popularity metric analysis
- **Rating Validation**: Minimum 10 votes threshold for rating reliability

### **4. Analytical Queries**

#### **A. Actor-Director Analysis**
- Bruce Willis in Sci-Fi/Action films
- Uma Thurman in Quentin Tarantino films

#### **B. Comparative Analysis**
- Franchise vs Standalone performance across multiple metrics
- Director performance rankings (movies, revenue, ratings)
- Franchise-specific statistics

#### **C. Visualization & Trends**
- Revenue vs Budget correlation
- Genre-based ROI analysis
- Popularity vs Rating relationships
- Yearly box office trends

---

##  Data Structure

### **Core DataFrame Columns:**
| Column | Description |
|--------|-------------|
| `id` | TMDb movie ID |
| `title` | Movie title |
| `tagline` | Movie tagline |
| `release_date` | Release date (datetime) |
| `genres` | Pipe-separated genres |
| `belongs_to_collection` | Franchise name (if applicable) |
| `original_language` | Original language code |
| `budget_musd` | Budget in millions USD |
| `revenue_musd` | Revenue in millions USD |
| `production_companies` | Pipe-separated companies |
| `production_countries` | Pipe-separated countries |
| `vote_count` | Number of votes |
| `vote_average` | Average rating |
| `popularity` | TMDb popularity score |
| `runtime` | Movie duration in minutes |
| `overview` | Plot summary |
| `spoken_languages` | Pipe-separated languages |
| `poster_path` | Poster image path |
| `cast` | List of cast members |
| `cast_size` | Number of cast members |
| `director` | Director name |
| `crew_size` | Number of crew members |

### **Derived Columns:**
- `budget_musd_num` - Numeric budget for calculations
- `revenue_musd_num` - Numeric revenue for calculations
- `profit_musd` - Calculated profit
- `roi` - Return on Investment ratio
- `movie_type` - Franchise or Standalone classification
- `year` - Extracted release year

---

##  Technical Implementation

### **Key Functions:**
1. **`extract_credits()`** - Processes cast/crew data from nested JSON
2. **`movie_kpis()`** - Unified function for all KPI calculations
3. **`best_directors()`** - Director performance analysis

### **Data Validation:**
- Missing value analysis for critical columns
- Data type consistency checks
- Filter application for meaningful comparisons (budget ≥ $10M, votes ≥ 10)

### **Visualization Suite:**
1. **Scatter Plots**: Budget vs Revenue, Popularity vs Rating
2. **Bar Charts**: Genre ROI, Franchise comparisons
3. **Line Charts**: Yearly revenue trends
4. **Comparative Visuals**: 2x2 grid for franchise analysis

---

## Key Insights

### **Financial Performance:**
- Clear correlation between budget and revenue
- Franchise films generally outperform standalone in revenue
- ROI varies significantly across genres

### **Audience Engagement:**
- Popularity doesn't always correlate with high ratings
- Franchise films receive more votes but similar average ratings

### **Production Insights:**
- Collection-based films have higher budgets
- Certain directors consistently deliver high-revenue films

---
##  Summary

This project: Cleans and restructures movie data
- Computes meaningful KPIs
- Performs deep analytical queries
- Compares franchise vs standalone performance
- Visualizes important industry trends

It serves as a complete workflow for **data extraction → transformation
→ analysis → visualization**.


## Setup & Usage

### **Prerequisites:**
```bash
pip install requests pandas  python-dotenv matplotlib