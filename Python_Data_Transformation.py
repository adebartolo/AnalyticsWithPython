# Transform the  messy data!

import pandas as pd
import re

class DataCleaner:
    def __init__(self, df):
        """Initializes the DataCleaner with a DataFrame."""
        self.df = df
    
    @staticmethod
    def remove_whitespace(text):
        """Removes leading and trailing whitespace from a string."""
        return text.strip() if isinstance(text, str) else text
    
    @staticmethod
    def to_lowercase(text):
        """Converts text to lowercase."""
        return text.lower() if isinstance(text, str) else text
    
    @staticmethod
    def remove_special_characters(text):
        """Removes special characters from a string."""
        return re.sub(r'[^A-Za-z0-9 ]+', '', text) if isinstance(text, str) else text
    
    def fill_missing_values(self, value):
        """Fills missing values in the DataFrame with a specified value."""
        self.df = self.df.fillna(value)
        return self
    
    def drop_duplicates(self):
        """Drops duplicate rows from the DataFrame."""
        self.df = self.df.drop_duplicates()
        return self
    
    def clean_column_names(self):
        """Cleans column names by making them lowercase and replacing spaces with underscores."""
        self.df.columns = [re.sub(r'\s+', '_', col.lower()) for col in self.df.columns]
        return self
    
    def apply_text_cleaning(self, column):
        """Applies whitespace removal and lowercase conversion to a specific column."""
        self.df[column] = self.df[column].apply(self.remove_whitespace).apply(self.to_lowercase)
        return self
    
    def clean_all_text_columns(self):
        """Applies text cleaning (whitespace & lowercase) to all string columns."""
        self.df = self.df.map(lambda x: self.remove_whitespace(x) if isinstance(x, str) else x)
        return self
    
    def get_dataframe(self):
        """Returns the cleaned DataFrame."""
        return self.df

# Fake data to test
data = {
    'Name': ['John', 'Mary', 'Sophia', 'David', 'Emily', 'Lucas', 'John', 'Emily', 'David', 'Sophia'],
    'Age': [29, 34, None, 22, 28, 25, 29, 28, 22, None]
}
df = pd.DataFrame(data)

cleaner = DataCleaner(df)
df_cleaned = (cleaner.clean_all_text_columns()
                     .fill_missing_values(0)
                     .drop_duplicates()
                     .clean_column_names()
                     .apply_text_cleaning('name')
                     .get_dataframe())

print(df_cleaned)
