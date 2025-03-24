import pandas as pd
from database import get_distinct_values, execute_query

# Get all entity names for the name filter dropdown
def get_name_options(db_path='math.db'):
    """Get a list of entity names for the name filter"""
    query = "SELECT DISTINCT name FROM math_entities ORDER BY name"
    result = execute_query(query, db_path=db_path)
    names = result['name'].tolist() if not result.empty else []
    return ["All"] + names

def get_entity_name_by_id(entity_id, db_path='math.db'):
    """Get the name of an entity by its ID"""
    if not entity_id:
        return None
    query = "SELECT name FROM math_entities WHERE id = ?"
    result = execute_query(query, params=(entity_id,), db_path=db_path)
    if not result.empty:
        return result['name'].iloc[0]
    return None

def get_entity_id_by_name(entity_name, db_path='math.db'):
    """Get the ID of an entity by its name"""
    if not entity_name:
        return None
    query = "SELECT id FROM math_entities WHERE name = ?"
    result = execute_query(query, params=(entity_name,), db_path=db_path)
    if not result.empty:
        return result['id'].iloc[0]
    return None

def get_course_options(db_path='math.db'):
    """Get a list of all courses in the database"""
    courses = get_distinct_values('math_entities', 'course', db_path)
    # Add "All" option at the beginning
    return ["All"] + courses

def get_type_options(db_path='math.db'):
    """Get a list of all entity types in the database"""
    types = get_distinct_values('math_entities', 'type', db_path)
    # Add "All" option at the beginning
    return ["All"] + types

def get_relationship_options(db_path='math.db'):
    """Get a list of all relationship types in the database"""
    relationships = get_distinct_values('relationships', 'relationship', db_path)
    # Add "All" option at the beginning
    return ["All"] + relationships

def get_tag_options(db_path='math.db'):
    """Get a list of all tags in the database"""
    tags = get_distinct_values('tags', 'tag', db_path)
    # Add "All" option at the beginning
    return ["All"] + tags

def get_parent_options(db_path='math.db'):
    """Get parent options for filtering"""
    query = """
    SELECT DISTINCT m1.id, m1.name 
    FROM math_entities m1
    JOIN math_entities m2 ON m1.id = m2.parent_id
    ORDER BY m1.name
    """
    result = execute_query(query, db_path=db_path)
    options = ["All", "Has Parent", "No Parent"]
    if not result.empty:
        parent_options = [f"{row['id']}: {row['name']}" for _, row in result.iterrows()]
        options.extend(parent_options)
    return options

def format_dataframe_for_display(df, table_name, db_path='math.db'):
    """Format a dataframe for display in Streamlit"""
    if df.empty:
        return df
    
    # Make a copy to avoid modifying the original
    formatted_df = df.copy()
    
    if table_name == 'math_entities':
        # Truncate long description fields
        if 'description' in formatted_df.columns:
            formatted_df['description'] = formatted_df['description'].apply(
                lambda x: x[:100] + '...' if x and len(x) > 100 else x
            )
        if 'latex_content' in formatted_df.columns:
            formatted_df['latex_content'] = formatted_df['latex_content'].apply(
                lambda x: x[:100] + '...' if x and len(x) > 100 else x
            )
        
        # Format parent ID to show name if available
        if 'parent_id' in formatted_df.columns:
            def format_parent(parent_id):
                if pd.isna(parent_id):
                    return None
                parent_name = get_entity_name_by_id(parent_id, db_path)
                if parent_name:
                    return f"{parent_name} (ID: {parent_id})"
                return parent_id
            
            formatted_df['parent'] = formatted_df['parent_id'].apply(format_parent)
            
            # Reorder columns to put parent after name
            if 'parent' in formatted_df.columns:
                cols = list(formatted_df.columns)
                parent_idx = cols.index('parent')
                parent_id_idx = cols.index('parent_id')
                # Remove parent_id from display
                cols.remove('parent_id')
                # Move parent column right after name
                name_idx = cols.index('name')
                cols.remove('parent')
                cols.insert(name_idx + 1, 'parent')
                formatted_df = formatted_df[cols]
    
    return formatted_df