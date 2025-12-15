import pandas as pd

def transform_movies(wanted_movies):
    
    
    # Convert list of dicts to DataFrame
    wanted_data = pd.DataFrame(wanted_movies)

    # Extract credits 
    def extract_credits(row):
        if not isinstance(row, dict):
            row = {}
        cast = row.get('cast') if isinstance(row.get('cast'), list) else []
        crew = row.get('crew') if isinstance(row.get('crew'), list) else []
        director = next((p.get('name') for p in crew if p.get('job') == "Director"), None)
        return pd.Series({
            'cast': cast,
            'cast_size': len(cast),
            'director': director,
            'crew_size': len(crew)
        })

    if 'credits' in wanted_data.columns:
        extracted_df = wanted_data['credits'].apply(extract_credits)
        wanted_data = pd.concat([wanted_data, extracted_df], axis=1)

    #  Drop unnecessary columns 
    drop_cols = ['adult', 'imdb_id', 'original_title', 'video', 'homepage']
    wanted_data = wanted_data.drop(columns=[col for col in drop_cols if col in wanted_data.columns])

    #  Flatten JSON fields 
    json_columns = ['belongs_to_collection', 'genres', 'production_companies', 'spoken_languages', 'production_countries']
    for col in json_columns:
        if col in wanted_data.columns:
            if col == 'belongs_to_collection':
                wanted_data[col] = wanted_data[col].apply(lambda x: x['name'] if isinstance(x, dict) else None)
            else:
                wanted_data[col] = wanted_data[col].apply(lambda x: "|".join([item['name'] for item in x]) if isinstance(x, list) else None)

    # Convert numeric columns
    numeric_cols = ["budget", "revenue", "id", "popularity"]
    for col in numeric_cols:
        if col in wanted_data.columns:
            wanted_data[col] = pd.to_numeric(wanted_data[col], errors='coerce').fillna(0).astype(int)

    #Convert release_date
    if 'release_date' in wanted_data.columns:
        wanted_data['release_date'] = pd.to_datetime(wanted_data['release_date'], errors='coerce')

    #Format budget/revenue
    for col in ["budget", "revenue"]:
        if col in wanted_data.columns:
            wanted_data[col] = wanted_data[col].apply(lambda x: f"${x/1_000_000:.1f}M")
            wanted_data.rename(columns={col: f"{col}_musd"}, inplace=True)

    # Reorder columns
    new_column_order = [
        'id', 'title', 'tagline', 'release_date', 'genres', 'belongs_to_collection',
        'original_language', 'budget_musd', 'revenue_musd', 'production_companies',
        'production_countries', 'vote_count', 'vote_average', 'popularity',
        'runtime', 'overview', 'spoken_languages', 'poster_path',
        'cast', 'cast_size', 'director', 'crew_size'
    ]

    # Keep only columns that exist
    new_column_order = [col for col in new_column_order if col in wanted_data.columns]
    wanted_data = wanted_data[new_column_order]

    # Reset index
    wanted_data.reset_index(drop=True, inplace=True)

    return wanted_data

