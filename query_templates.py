# Query templates for the math database

# Basic table queries
MATH_ENTITIES_QUERY = """
SELECT * FROM math_entities
WHERE 1=1
{type_filter}
{course_filter}
{name_filter}
{parent_filter}
ORDER BY id
"""

RELATIONSHIPS_QUERY = """
SELECT 
    r.id,
    m1.name as subject_name, 
    r.relationship,
    m2.name as object_name,
    r.description,
    r.subject_id,
    r.object_id
FROM relationships r
JOIN math_entities m1 ON r.subject_id = m1.id
JOIN math_entities m2 ON r.object_id = m2.id
WHERE 1=1
{relationship_filter}
{subject_filter}
{object_filter}
ORDER BY r.id
"""

TAGS_QUERY = """
SELECT 
    t.id,
    m.name as entity_name,
    t.tag,
    t.entity_id
FROM tags t
JOIN math_entities m ON t.entity_id = m.id
WHERE 1=1
{tag_filter}
{entity_filter}
ORDER BY t.id
"""

# Helper functions to build WHERE clauses
def build_type_filter(type_value):
    if type_value and type_value != "All":
        return f" AND type = '{type_value}'"
    return ""

def build_course_filter(course_value):
    if course_value and course_value != "All":
        return f" AND course = '{course_value}'"
    return ""

def build_name_filter(name_value):
    if name_value:
        return f" AND name LIKE '%{name_value}%'"
    return ""

def build_parent_filter(parent_value):
    if parent_value and parent_value != "None":
        if parent_value == "Has Parent":
            return f" AND parent_id IS NOT NULL"
        elif parent_value == "No Parent":
            return f" AND parent_id IS NULL"
        elif parent_value and ":" in parent_value:
            # Extract the ID from "ID: Name" format
            parent_id = parent_value.split(":")[0].strip()
            return f" AND parent_id = {parent_id}"
    return ""

def build_relationship_filter(relationship_value):
    if relationship_value and relationship_value != "All":
        return f" AND relationship = '{relationship_value}'"
    return ""

def build_subject_filter(subject_value):
    if subject_value and subject_value != "All":
        try:
            # First try to parse as ID
            subject_id = int(subject_value)
            return f" AND r.subject_id = {subject_id}"
        except ValueError:
            # If not an ID, search by name
            return f" AND m1.name LIKE '%{subject_value}%'"
    return ""

def build_object_filter(object_value):
    if object_value and object_value != "All":
        try:
            # First try to parse as ID
            object_id = int(object_value)
            return f" AND r.object_id = {object_id}"
        except ValueError:
            # If not an ID, search by name
            return f" AND m2.name LIKE '%{object_value}%'"
    return ""

def build_tag_filter(tag_value):
    if tag_value and tag_value != "All":
        return f" AND tag = '{tag_value}'"
    return ""

def build_entity_filter(entity_value):
    if entity_value and entity_value != "All":
        try:
            # First try to parse as ID
            entity_id = int(entity_value)
            return f" AND t.entity_id = {entity_id}"
        except ValueError:
            # If not an ID, search by name
            return f" AND m.name LIKE '%{entity_value}%'"
    return ""

# Function to build complete queries
def get_filtered_entities_query(type_value=None, course_value=None, name_value=None, parent_value=None):
    type_filter = build_type_filter(type_value)
    course_filter = build_course_filter(course_value)
    name_filter = build_name_filter(name_value)
    parent_filter = build_parent_filter(parent_value)
    
    return MATH_ENTITIES_QUERY.format(
        type_filter=type_filter,
        course_filter=course_filter,
        name_filter=name_filter,
        parent_filter=parent_filter
    )

def get_filtered_relationships_query(relationship_value=None, subject_value=None, object_value=None):
    relationship_filter = build_relationship_filter(relationship_value)
    subject_filter = build_subject_filter(subject_value)
    object_filter = build_object_filter(object_value)
    
    return RELATIONSHIPS_QUERY.format(
        relationship_filter=relationship_filter,
        subject_filter=subject_filter,
        object_filter=object_filter
    )

def get_filtered_tags_query(tag_value=None, entity_value=None):
    tag_filter = build_tag_filter(tag_value)
    entity_filter = build_entity_filter(entity_value)
    
    return TAGS_QUERY.format(
        tag_filter=tag_filter,
        entity_filter=entity_filter
    )
