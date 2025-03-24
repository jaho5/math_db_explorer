import streamlit as st
import pandas as pd
from database import execute_query

def display_search_page(db_path='math.db'):
    """
    Display a comprehensive search interface for the mathematics database
    """
    st.title("Search Mathematical Content")
    st.markdown("""
    Search across all mathematical entities, relationships, and tags in the database.
    This search page looks for your query in names, descriptions, latex content, and tags.
    """)
    
    # Search input
    search_query = st.text_input("Enter search term:", 
                                help="Search in names, descriptions, latex content, and tags")
    
    # Search options
    col1, col2 = st.columns(2)
    
    with col1:
        search_in = st.multiselect(
            "Search in:",
            options=["Names", "Descriptions", "LaTeX Content", "Tags"],
            default=["Names", "Descriptions", "Tags"]
        )
        
        case_sensitive = st.checkbox("Case sensitive", value=False)
    
    with col2:
        entity_types = st.multiselect(
            "Entity types:",
            options=["concept", "property", "theorem", "proof", "proof_step", 
                     "definition", "exercise", "lemma", "corollary"],
            default=[]
        )
        
        courses = st.multiselect(
            "Courses:",
            options=get_course_list(db_path),
            default=[]
        )
    
    # Execute search
    if st.button("Search") or search_query:
        if not search_query:
            st.warning("Please enter a search term")
            return
        
        # Perform search
        results = perform_search(
            search_query, 
            search_in, 
            entity_types, 
            courses, 
            case_sensitive,
            db_path
        )
        
        # Display results
        if not results.empty:
            st.success(f"Found {len(results)} results matching '{search_query}'")
            st.dataframe(results, use_container_width=True)
            
            # Option to view entity
            if st.checkbox("View entity details", value=False):
                entity_id = st.selectbox(
                    "Select entity to view:",
                    options=[f"{row['id']}: {row['name']} ({row['type']})" for _, row in results.iterrows()]
                )
                
                if entity_id:
                    # Extract ID from the string
                    id_num = int(entity_id.split(':')[0].strip())
                    
                    # Display entity details
                    display_entity_details(id_num, db_path)
        else:
            st.info(f"No results found for '{search_query}'")
            
            # Suggestion for similar terms
            suggest_similar_terms(search_query, db_path)

def get_course_list(db_path):
    """Get list of available courses from the database"""
    query = "SELECT DISTINCT course FROM math_entities WHERE course IS NOT NULL ORDER BY course"
    result = execute_query(query, db_path=db_path)
    return result['course'].tolist() if not result.empty else []

def perform_search(query, search_in, entity_types, courses, case_sensitive, db_path):
    """
    Execute search across different fields based on user options
    
    Args:
        query: The search term
        search_in: List of fields to search in
        entity_types: List of entity types to include
        courses: List of courses to include
        case_sensitive: Whether to do a case-sensitive search
        db_path: Path to the database
    
    Returns:
        DataFrame with search results
    """
    # Prepare the LIKE operation based on case sensitivity
    if case_sensitive:
        like_op = "LIKE"
    else:
        like_op = "LIKE"
        query = query.lower()
    
    # Build WHERE clauses for search fields
    search_clauses = []
    
    if "Names" in search_in:
        if case_sensitive:
            search_clauses.append(f"e.name {like_op} '%{query}%'")
        else:
            search_clauses.append(f"LOWER(e.name) {like_op} '%{query}%'")
    
    if "Descriptions" in search_in:
        if case_sensitive:
            search_clauses.append(f"e.description {like_op} '%{query}%'")
        else:
            search_clauses.append(f"LOWER(e.description) {like_op} '%{query}%'")
    
    if "LaTeX Content" in search_in:
        if case_sensitive:
            search_clauses.append(f"e.latex_content {like_op} '%{query}%'")
        else:
            search_clauses.append(f"LOWER(e.latex_content) {like_op} '%{query}%'")
    
    # Build WHERE clauses for entity types
    type_clause = ""
    if entity_types:
        type_conditions = ", ".join([f"'{t}'" for t in entity_types])
        type_clause = f"AND e.type IN ({type_conditions})"
    
    # Build WHERE clauses for courses
    course_clause = ""
    if courses:
        course_conditions = ", ".join([f"'{c}'" for c in courses])
        course_clause = f"AND e.course IN ({course_conditions})"
    
    # Build the query for entity search (excluding tags)
    entity_search_conditions = " OR ".join(search_clauses) if search_clauses else "1=0"
    entity_query = f"""
    SELECT e.id, e.name, e.type, e.course, 'Entity Match' as match_type
    FROM math_entities e
    WHERE ({entity_search_conditions})
    {type_clause}
    {course_clause}
    """
    
    # Build the query for tag search
    tag_query = ""
    if "Tags" in search_in:
        tag_query = f"""
        UNION
        SELECT e.id, e.name, e.type, e.course, 'Tag Match' as match_type
        FROM math_entities e
        JOIN tags t ON e.id = t.entity_id
        WHERE {'' if case_sensitive else 'LOWER('}t.tag{'' if case_sensitive else ')'} {like_op} '%{query}%'
        {type_clause}
        {course_clause}
        """
    
    # Combine queries and execute
    full_query = f"""
    {entity_query}
    {tag_query}
    ORDER BY name
    """
    
    try:
        results = execute_query(full_query, db_path=db_path)
        return results
    except Exception as e:
        st.error(f"Error executing search: {str(e)}")
        return pd.DataFrame()

def display_entity_details(entity_id, db_path):
    """
    Display detailed information about a selected entity
    
    Args:
        entity_id: ID of the entity to display
        db_path: Path to the database
    """
    query = f"SELECT * FROM math_entities WHERE id = {entity_id}"
    entity = execute_query(query, db_path=db_path)
    
    if entity.empty:
        st.error(f"Entity with ID {entity_id} not found")
        return
    
    # Display entity details
    entity = entity.iloc[0]  # Get the first row
    
    st.markdown("---")
    st.subheader(f"{entity['name']} ({entity['type']})")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Basic Information**")
        st.write(f"**ID:** {entity['id']}")
        st.write(f"**Type:** {entity['type']}")
        st.write(f"**Course:** {entity['course']}")
        
        # Get parent information if applicable
        if pd.notna(entity['parent_id']):
            parent_query = f"SELECT name FROM math_entities WHERE id = {entity['parent_id']}"
            parent = execute_query(parent_query, db_path=db_path)
            if not parent.empty:
                st.write(f"**Parent:** {parent['name'].iloc[0]}")
        
        # Get tags
        tags_query = f"SELECT tag FROM tags WHERE entity_id = {entity['id']}"
        tags = execute_query(tags_query, db_path=db_path)
        if not tags.empty:
            tag_list = tags['tag'].tolist()
            st.write(f"**Tags:** {', '.join(tag_list)}")
    
    with col2:
        st.markdown("**Content**")
        
        if pd.notna(entity['description']):
            st.markdown("**Description:**")
            st.write(entity['description'])
        
        if pd.notna(entity['latex_content']):
            st.markdown("**LaTeX Content:**")
            st.write(entity['latex_content'])
    
    # Show relationships
    st.markdown("**Relationships**")
    
    # Outgoing relationships
    outgoing_query = f"""
    SELECT r.relationship, m.name, m.type
    FROM relationships r
    JOIN math_entities m ON r.object_id = m.id
    WHERE r.subject_id = {entity['id']}
    """
    outgoing = execute_query(outgoing_query, db_path=db_path)
    
    if not outgoing.empty:
        st.markdown("**This entity relates to:**")
        for _, rel in outgoing.iterrows():
            st.write(f"- {rel['relationship']} → {rel['name']} ({rel['type']})")
    
    # Incoming relationships
    incoming_query = f"""
    SELECT r.relationship, m.name, m.type
    FROM relationships r
    JOIN math_entities m ON r.subject_id = m.id
    WHERE r.object_id = {entity['id']}
    """
    incoming = execute_query(incoming_query, db_path=db_path)
    
    if not incoming.empty:
        st.markdown("**Related to this entity:**")
        for _, rel in incoming.iterrows():
            st.write(f"- {rel['name']} ({rel['type']}) → {rel['relationship']}")

def suggest_similar_terms(query, db_path):
    """
    Suggest similar terms when no results are found
    
    Args:
        query: The original search query
        db_path: Path to the database
    """
    # Try to find terms that contain parts of the query
    words = query.split()
    
    if len(words) > 1:
        st.markdown("**Try searching for:**")
        for word in words:
            if len(word) > 3:  # Only suggest words with sufficient length
                st.write(f"- {word}")
    
    # Suggest similar mathematical terms
    if len(query) > 3:
        # Look for similar terms in the database
        similar_query = f"""
        SELECT name FROM math_entities
        WHERE name LIKE '%{query[:3]}%'
        GROUP BY name
        ORDER BY name
        LIMIT 5
        """
        similar_results = execute_query(similar_query, db_path=db_path)
        
        if not similar_results.empty:
            st.markdown("**Similar mathematical terms:**")
            for _, row in similar_results.iterrows():
                st.write(f"- {row['name']}")

if __name__ == "__main__":
    display_search_page()
