import streamlit as st
import pandas as pd
import sqlite3
from database import execute_query, get_all_tables
from query_templates import (
    get_filtered_entities_query, 
    get_filtered_relationships_query, 
    get_filtered_tags_query
)
from utils import (
    get_course_options, 
    get_type_options,
    get_relationship_options,
    get_tag_options,
    get_parent_options,
    get_name_options,
    format_dataframe_for_display,
    get_entity_name_by_id
)
from data_management import display_import_export_page

# Page configuration
st.set_page_config(
    page_title="Math Database Explorer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Check if db exists and show error if not
def validate_db_path(path):
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        if not tables:
            st.error(f"Database at {path} exists but contains no tables.")
            return False
        return True
    except Exception as e:
        st.error(f"Could not connect to database at {path}. Error: {str(e)}")
        return False

# Add database path configuration
db_path = st.sidebar.text_input("Database Path", value="math.db")

# Validate database
db_valid = validate_db_path(db_path)

# Create sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Browse Entities", "Import/Export Data"]
)

# Title banner
st.title("Math Database Explorer 📚")

# Different pages based on selection
if db_valid:
    if page == "Browse Entities":
        # Original Browse Entities functionality
        st.markdown("""
        This application allows you to explore the mathematics database, view concepts, 
        theorems, proofs, and the relationships between different mathematical entities.
        """)
        
        # Create tabs for different tables
        table_tabs = st.tabs(["Math Entities", "Relationships", "Tags"])
        
        # Math Entities Tab
        with table_tabs[0]:
            st.header("Mathematical Entities")
            
            # Filters in columns for better layout
            col1, col2 = st.columns(2)
            
            with col1:
                type_filter = st.selectbox(
                    "Filter by Type",
                    options=get_type_options(db_path),
                    key="entity_type"
                )
                
                # Use db_path explicitly in all filter options
                name_filter = st.selectbox(
                    "Filter by Name",
                    options=get_name_options(db_path),
                    key="entity_name"
                )
            
            with col2:
                course_filter = st.selectbox(
                    "Filter by Course",
                    options=get_course_options(db_path),
                    key="entity_course"
                )
                
                parent_filter = st.selectbox(
                    "Filter by Parent",
                    options=get_parent_options(db_path),
                    key="entity_parent"
                )
            
            # Process parent_id if it's a numeric option
            if parent_filter and ":" in parent_filter:
                parent_id = parent_filter.split(":")[0].strip()
            else:
                parent_id = parent_filter
            
            # Process name filter - make sure we pass db_path to get entity name
            if name_filter == "All":
                name_filter = None
            
            # Build and execute query
            query = get_filtered_entities_query(
                type_value=type_filter,
                course_value=course_filter,
                name_value=name_filter,
                parent_value=parent_id
            )
            
            try:
                entities_df = execute_query(query, db_path=db_path)
                
                # Display the data
                if not entities_df.empty:
                    # Format for display
                    display_df = format_dataframe_for_display(entities_df, 'math_entities', db_path)
                    
                    # Show result count
                    st.write(f"Found {len(entities_df)} entities matching your criteria.")
                    
                    # Display the table
                    st.dataframe(display_df, use_container_width=True)
                    
                    # Detail view for selected entity
                    if st.checkbox("Show detailed view of selected entity", value=True):
                        # Search entities by name for a more user-friendly experience
                        entity_search = st.text_input("Search entity by name:", key="entity_detail_search")
                        if entity_search:
                            entity_search_query = f"SELECT id, name FROM math_entities WHERE name LIKE '%{entity_search}%' ORDER BY name LIMIT 10"
                            entity_search_results = execute_query(entity_search_query, db_path=db_path)
                            if not entity_search_results.empty:
                                entity_options = [f"{row['id']}: {row['name']}" for _, row in entity_search_results.iterrows()]
                                selected_entity = st.selectbox("Select entity:", options=entity_options, key="entity_select")
                                if selected_entity:
                                    entity_id = int(selected_entity.split(":")[0].strip())
                                    # Continue with existing code for showing details
                            else:
                                st.warning(f"No entities found matching '{entity_search}'")
                                entity_id = None
                        else:
                            entity_id = None
                        
                        # Still provide a direct ID input option for advanced users
                        if not entity_id:
                            show_id_input = st.checkbox("Or enter entity ID directly", value=False)
                            if show_id_input:
                                entity_id = st.number_input("Enter entity ID", min_value=1, step=1)
                        
                        if entity_id:
                            detailed_query = f"SELECT * FROM math_entities WHERE id = {entity_id}"
                            entity_detail = execute_query(detailed_query, db_path=db_path)
                            
                            if not entity_detail.empty:
                                st.subheader(f"Details for: {entity_detail['name'].iloc[0]}")
                                
                                # Display entity details
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("**Basic Information**")
                                    st.write(f"**ID:** {entity_detail['id'].iloc[0]}")
                                    st.write(f"**Name:** {entity_detail['name'].iloc[0]}")
                                    st.write(f"**Type:** {entity_detail['type'].iloc[0]}")
                                    st.write(f"**Course:** {entity_detail['course'].iloc[0]}")
                                    
                                    # Handle parent relationship
                                    parent_id = entity_detail['parent_id'].iloc[0]
                                    if pd.notna(parent_id):
                                        parent_name = get_entity_name_by_id(parent_id, db_path)
                                        st.write(f"**Parent:** {parent_name} (ID: {parent_id})")
                                    
                                    if 'sequence_num' in entity_detail.columns and pd.notna(entity_detail['sequence_num'].iloc[0]):
                                        st.write(f"**Sequence Number:** {entity_detail['sequence_num'].iloc[0]}")
                                
                                with col2:
                                    st.markdown("**Content**")
                                    if 'description' in entity_detail.columns and pd.notna(entity_detail['description'].iloc[0]):
                                        st.markdown("**Description:**")
                                        st.write(entity_detail['description'].iloc[0])
                                    
                                    if 'latex_content' in entity_detail.columns and pd.notna(entity_detail['latex_content'].iloc[0]):
                                        st.markdown("**LaTeX Content:**")
                                        st.markdown(entity_detail['latex_content'].iloc[0])
                                
                                # Show related entities
                                st.markdown("**Related Entities**")
                                
                                # Find relationships where this entity is the subject
                                subject_query = f"""
                                SELECT r.relationship, m.name, m.type, r.description
                                FROM relationships r
                                JOIN math_entities m ON r.object_id = m.id
                                WHERE r.subject_id = {entity_id}
                                """
                                subject_relations = execute_query(subject_query, db_path=db_path)
                                
                                if not subject_relations.empty:
                                    st.markdown("**Outgoing Relationships:**")
                                    # Format for display - focus on the relationship and related entity
                                    formatted_relations = subject_relations.rename(columns={
                                        'name': 'Related Entity',
                                        'type': 'Entity Type',
                                        'relationship': 'Relationship',
                                        'description': 'Description'
                                    })
                                    st.dataframe(formatted_relations, use_container_width=True)
                                
                                # Find relationships where this entity is the object
                                object_query = f"""
                                SELECT r.relationship, m.name, m.type, r.description
                                FROM relationships r
                                JOIN math_entities m ON r.subject_id = m.id
                                WHERE r.object_id = {entity_id}
                                """
                                object_relations = execute_query(object_query, db_path=db_path)
                                
                                if not object_relations.empty:
                                    st.markdown("**Incoming Relationships:**")
                                    # Format for display - focus on the relationship and related entity
                                    formatted_relations = object_relations.rename(columns={
                                        'name': 'Related Entity',
                                        'type': 'Entity Type',
                                        'relationship': 'Relationship',
                                        'description': 'Description'
                                    })
                                    st.dataframe(formatted_relations, use_container_width=True)
                                
                                # Find tags for this entity
                                tags_query = f"SELECT tag FROM tags WHERE entity_id = {entity_id}"
                                tags = execute_query(tags_query, db_path=db_path)
                                
                                if not tags.empty:
                                    st.markdown("**Tags:**")
                                    st.write(", ".join(tags['tag'].tolist()))
                            else:
                                st.warning(f"No entity found with ID {entity_id}")
                else:
                    st.info("No entities found with the current filters.")
            except Exception as e:
                st.error(f"Error querying the database: {str(e)}")
        
        # Relationships Tab
        with table_tabs[1]:
            st.header("Relationships Between Entities")
            
            # Filters in columns
            col1, col2 = st.columns(2)
            
            with col1:
                relationship_filter = st.selectbox(
                    "Filter by Relationship Type",
                    options=get_relationship_options(db_path),
                    key="rel_type"
                )
            
            with col2:
                subject_filter = st.text_input(
                    "Filter by Subject (name or ID)",
                    key="subject_id"
                )
                
                object_filter = st.text_input(
                    "Filter by Object (name or ID)",
                    key="object_id"
                )
            
            # Build and execute query
            query = get_filtered_relationships_query(
                relationship_value=relationship_filter,
                subject_value=subject_filter,
                object_value=object_filter
            )
            
            try:
                relationships_df = execute_query(query, db_path=db_path)
                
                # Display the data
                if not relationships_df.empty:
                    # Show result count
                    st.write(f"Found {len(relationships_df)} relationships matching your criteria.")
                    
                    # Display the table
                    st.dataframe(relationships_df, use_container_width=True)
                else:
                    st.info("No relationships found with the current filters.")
            except Exception as e:
                st.error(f"Error querying the database: {str(e)}")
        
        # Tags Tab
        with table_tabs[2]:
            st.header("Entity Tags")
            
            # Filters
            col1, col2 = st.columns(2)
            
            with col1:
                tag_filter = st.selectbox(
                    "Filter by Tag",
                    options=get_tag_options(db_path),
                    key="tag_value"
                )
            
            with col2:
                entity_filter = st.text_input(
                    "Filter by Entity (name or ID)",
                    key="tag_entity_id"
                )
            
            # Build and execute query
            query = get_filtered_tags_query(
                tag_value=tag_filter,
                entity_value=entity_filter
            )
            
            try:
                tags_df = execute_query(query, db_path=db_path)
                
                # Display the data
                if not tags_df.empty:
                    # Show result count
                    st.write(f"Found {len(tags_df)} tags matching your criteria.")
                    
                    # Display the table
                    st.dataframe(tags_df, use_container_width=True)
                else:
                    st.info("No tags found with the current filters.")
            except Exception as e:
                st.error(f"Error querying the database: {str(e)}")
    
    elif page == "Import/Export Data":
        display_import_export_page(db_path)

else:
    st.error("Please provide a valid database path in the sidebar.")
    st.info("The application needs a valid SQLite database with the required tables: math_entities, relationships, and tags.")

# Footer
st.markdown("---")
st.markdown("Math Database Explorer | Created with Streamlit")
