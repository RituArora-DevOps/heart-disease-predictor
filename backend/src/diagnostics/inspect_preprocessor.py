import dill
import os
import numpy as np

PREPROCESSOR_PATH = os.path.join('artifacts', 'preprocessor.pkl')

def inspect_ordinal_mappings():
    """Loads the preprocessor artifact and extracts the category order for ordinal features."""
    try:
        # 1. Load the preprocessor artifact
        preprocessor = dill.load(open(PREPROCESSOR_PATH, 'rb'))
        print("Preprocessor loaded successfully.")

        print("\n--- EXTRACTING ORDINAL MAPPING FROM COLUMNTRANSFORMER ---")
        
        found_ordinal = False
        
        # 2. Iterate through each defined transformation pipeline (transformer)
        for name, pipeline, features in preprocessor.transformers_:
            # Check if the pipeline contains a step with an OrdinalEncoder
            if hasattr(pipeline, 'steps'):
                for step_name, step_transformer in pipeline.steps:
                    if 'ordinal' in step_name.lower() or 'encoder' in step_name.lower():
                        if hasattr(step_transformer, 'categories_'):
                            found_ordinal = True
                            print(f"\nFound OrdinalEncoder in pipeline: '{name}'")
                            
                            categories = step_transformer.categories_
                            
                            # 3. Print the exact mapping for each relevant feature
                            for i, feature in enumerate(features):
                                # Filter for the features used in your engineered interactions
                                if feature in ['Age_Category', 'General_Health', 'Exercise']:
                                    print(f"  Feature: {feature}")
                                    print(f"    Assigned Categories (Index 0 is the lowest numerical value):")
                                    
                                    # This shows the EXACT mapping the model used (Index j is the assigned score)
                                    for j, category in enumerate(categories[i]):
                                        print(f"      Score {j}: {category}")
                                    print("-" * 20)

        if not found_ordinal:
            print("Warning: Could not automatically find the OrdinalEncoder. Check your ColumnTransformer structure.")

    except FileNotFoundError:
        print(f"Error: Preprocessor file not found at {PREPROCESSOR_PATH}")
    except Exception as e:
        print(f"An error occurred during inspection: {e}")

if __name__ == '__main__':
    inspect_ordinal_mappings()