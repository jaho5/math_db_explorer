# Math Database Explorer

An interactive web application for exploring and managing a mathematical knowledge database.

## Project Overview

The Math Database Explorer is a Streamlit-based application designed to help users navigate and interact with a structured database of mathematical knowledge. The database organizes mathematical concepts, properties, theorems, proofs, and their relationships in a searchable format.

## Features

- **Browse Mathematical Entities**: View and filter concepts, theorems, proofs, and other mathematical entities.

## Database Structure

The database consists of three main tables:

1. **math_entities**: Contains all mathematical objects (concepts, theorems, proofs, steps, exercises)
2. **relationships**: Stores connections between math entities
3. **tags**: Maintains searchable keywords for entities

### Entity Types

The system supports various mathematical entity types:

- **concept**: Fundamental mathematical ideas
- **property**: Characteristics of concepts
- **theorem**: Mathematical statements proven to be true
- **proof**: Complete proof of a theorem
- **proof_step**: Individual logical step within a proof
- **definition**: Formal explanation of a concept
- **exercise**: Problem for practice
- **lemma**: Helper theorem used in larger proofs
- **corollary**: Direct result of a theorem

### Relationship Types

Common relationship types include:

- **has_property**: Connects a concept to its properties
- **implies**: Shows logical implication
- **equivalent_to**: Shows logical equivalence
- **uses**: A proof step uses a concept/theorem
- **generalizes**: One concept extends another
- **specializes**: One concept is a special case of another
- **prerequisite_for**: Concept needed to understand another
- **part_of**: Entity is a component of another
- **derived_from**: One result comes from another
- **example_of**: Specific instance of a concept

## Installation

1. Clone this repository
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. Start the application and provide the path to your SQLite database in the sidebar.
2. Use the tabs to navigate between Math Entities, Relationships, and Tags.
3. Apply filters to narrow down your search.
4. Click on the "Show detailed view" checkbox to see comprehensive information about a selected entity.

## Contributing

Contributions to improve the Math Database Explorer are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is open source and available under the MIT License.
