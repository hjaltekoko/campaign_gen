import streamlit as st
import pandas as pd
import io
from collections import Counter
import itertools
from oauth2client.service_account import ServiceAccountCredentials
import gspread

category_mapping = {
    "Kids Clothes": "Børnetøj",
    "Kids Shoes": "Børnesko",
    "Kids Toys": "Legetøj",
    "Kids Home": "Til Børneværelset",
    "Mens Fashion": "Herretøj",
    "Mens Jeans": "Herrebukser",
    "Mens Shoes": "Herresko",
    "Mens Casual": "Herretøj",
    "Mens Shirts": "Skjorter",
    "Mens Underwear & Socks": "Herreundertøj",
    "Mens Leather & Access": "Accessories",
    "Womens Contemporary Fashion": "Dametøj",
    "Womens Fast Fashion": "Dametøj",
    "Womens Urban": "Dametøj",
    "Womens Jeans": "Damebukser",
    "Womens Fashion": "Dametøj",
    "Womens Shoes": "Damesko",
    "Womens Modern Classic": "Dametøj",
    "Lingerie & Swim": "Lingeri",
    "Loungewear": "Loungewear",
    "Stockings": "Stockings",
    "Jewellery & Sunglasses": "Accessories",
    "Contemporary Bags": "Tasker",
    "Scarves & Hats": "Accessories",
    "Living": "Interiør",
    "Lamps": "Lamper",
    "Small Electricals": "Elektronik",
    "Kitchen & Tabletop": "Køkkenudstyr",
    "Modern Design": "Interiør",
    "Bath": "Bolig",
    "Bed": "Bolig",
    "Body & Beauty": "Skønhed",
    "Skincare": "Hudpleje",
    "Makeup": "Makeup",
    "Perfume": "Parfume",
    "Travel & Active": "Sport",
    "Foodhall": "Delikatesser",
    "Confectionery": "Slik"
}


# Initial templates
HEADLINES_DANISH = {
    "Headline 2": [
        "{rabat} til Super Bazaar i Magasin",
        "20-50% på masser af brands"
    ],
    "Headline 3": [
        "Spar {rabat} på {brand}",
        "Spar {rabat}"
    ],
    "Headline 4": [
        "Få {rabat} på {brand}",
        "Få {rabat}"
    ],
    "Headline 5": [
        "{rabat} på {brand}",
        "{rabat} i Magasin"
    ],
    "Headline 6": [
        "Tilbud på {brand} til Super Bazaar",
        "Super Bazaar-tilbud på {brand}",
        "{rabat} på {brand} til Super Bazaar",
        "Tilbud på masser af {brand}",
        "Tilbud til Super Bazaar",
    ],
    "Headline 7": lambda row: [
        "Multiday" if row['period'] in [14, 7] else
        "One day" if row['period'] in ["Torsdag","Fredag","Lørdag","Søndag"] else
    ""
    ],
    "Headline 8": lambda row: [
        "Gælder til d. 3./4." if row['period'] in ["14", 14] else
        "Gælder til d. 27./3." if row['period'] in ["7", 7] else
        "Gælder kun d. 21." if row['period'] == "Torsdag" else
        "Gælder kun d. 22." if row['period'] == "Fredag" else
        "Gælder kun d. 23." if row['period'] == "Lørdag" else
        "Gælder kun d. 24." if row['period'] == "Søndag" else
        ""
    ]
}
DESCRIPTIONS_DANISH = {
    "Description 1": [
        "Kom til Super Bazaar i Magasin og få {rabat} på {brand}",
    ],
    "Description 2": [
        "Lige nu får du {rabat} på {brand} - {Headline 8}",
    ],
}
HEADLINES_SWEDISH = {
    "Headline 2": [  # Add your Swedish templates here
        "{rabat} på {brand}",
        "{rabat} - {brand}",
        "Massor av bra erbjudanden"
    ],
    "Headline 3": [  # Add more Swedish templates here
        "Få {rabat} på {brand}",
        "Få {rabat} - {brand}",
        "Få {rabat}",
    ],
    "Headline 4": [  # Add more Swedish templates here
        "Spara {rabat} på {brand}",
        "Spara {rabat} - {brand}",
        "Spara {rabat}",
    ],
    "Headline 5": [  # Add more Swedish templates here
        "{rabat} på Mid Season Sale",
    ],
    "Headline 6": [  # Add more Swedish templates here
        "Köp {brand} på Mid Season Sale",
        "{brand} på Mid Season Sale",
        "Mid Season Sale-erbjudanden",
    ],
    "Headline 7": lambda row: [
        "Multiday" if row['period'] in [14, 7] else
        "One day" if row['period'] in ["Torsdag","Fredag","Lørdag","Søndag"] else
    ""
    ],
    "Headline 8": lambda row: [
        "Gäller fram till den 3/4" if row['period'] in ["14", 14] else
        "Gäller fram till den 27/3" if row['period'] in ["7", 7] else
        "Gäller bara idag den 21/3" if row['period'] == "Torsdag" else
        "Gäller bara idag den 22/3" if row['period'] == "Fredag" else
        "Gäller bara idag den 23/3" if row['period'] == "Lørdag" else
        "Gäller bara idag den 24/3" if row['period'] == "Søndag" else
        ""
    ]
}
DESCRIPTIONS_SWEDISH = {
    "Description 1": [
        "Just nu får du {rabat} på {brand} på Magasin.se",
    ],
    "Description 2": [
        "Mid Season Sale är i gång med 20-50% på tusentals märkesvaror",
    ],
}

# Mapping for creating labels based on the 'period' column
period_label_mapping = {
    14: "sb_14_day",
    7: "sb_7_day",
    "Torsdag": "sb_tor_oneday",
    "Fredag": "sb_fre_oneday",
    "Lørdag": "sb_loer_oneday",
    "Søndag": "sb_soen_oneday"
}
# Mapping for creating communication variable based on the 'period' column
period_type_mapping = {
    4: "T.o.m. søndag",
    1: "Kun i dag",
}


# Set up credentials
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# Retrieve the secrets from st.secrets
secrets_dict = {
    "type": st.secrets["type"],
    "project_id": st.secrets["project_id"],
    "private_key_id": st.secrets["private_key_id"],
    "private_key": st.secrets["private_key"],
    "client_email": st.secrets["client_email"],
    "client_id": st.secrets["client_id"],
    "auth_uri": st.secrets["auth_uri"],
    "token_uri": st.secrets["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["client_x509_cert_url"],
    # Add any other fields you have in secrets.toml
}

# Use the from_json_keyfile_dict method
creds = ServiceAccountCredentials.from_json_keyfile_dict(secrets_dict, scope)
client = gspread.authorize(creds)


def generate_texts(df, headlines, descriptions):
    df.rename(columns={"Rabat%_y": "period"}, inplace=True)
    df.rename(columns={"Ws navn": "brand"}, inplace=True)
    df.rename(columns={"Rabat%_x": "rabat"}, inplace=True)
    
    # Define a function to check whether a string represents a valid percentage
    def is_percentage(s):
        if not isinstance(s, str):
            return False
        if s.endswith('%'):
            try:
                float(s.rstrip('%'))
                return True
            except ValueError:
                return False
        return False
    
    # Replace non-percentage 'rabat' values with "20-50%"
    df.loc[~df['rabat'].apply(is_percentage), 'rabat'] = "20-50%"
    df["type"] = df["period"].map(period_type_mapping)

    def generate_ad_text(row, templates, threshold):
        if callable(templates):  # Check if the templates are a function (lambda)
            templates = templates(row)  # Call the function to get the actual templates
        
        possible_texts = [template.format(**row) for template in templates]
        
        # Filter valid texts based on the threshold
        valid_texts = [text for text in possible_texts if len(text) <= threshold]
        
        # Separate valid texts into two lists: one including the brand variable and the other one not
        brand_included_texts = [text for text in valid_texts if row['brand'] in text]
        brand_not_included_texts = [text for text in valid_texts if row['brand'] not in text]
        
        # Prioritize texts with the brand variable, if any
        if brand_included_texts:
            return max(brand_included_texts, key=len, default="")
        else:
            return max(brand_not_included_texts, key=len, default="")

    # Generating Headlines
    for column_name, templates in headlines.items():
        df[column_name] = df.apply(lambda row: generate_ad_text(row, templates, 30), axis=1)

    # Generating Descriptions
    for column_name, templates in descriptions.items():
        df[column_name] = df.apply(lambda row: generate_ad_text(row, templates, 90), axis=1)

    df["label"] = df["period"].map(period_label_mapping)

    return df


def display_and_edit_templates(templates_dict, threshold):
    edited_templates_dict = {}
    for headline, templates in templates_dict.items():
        if callable(templates):
            edited_templates_dict[headline] = templates
            continue
        st.subheader(f"Templates for {headline}")
        edited_templates = []
        for template in templates:
            edited_template = st.text_input(f"Template (Recommended max {threshold} chars)", value=template)
            if len(edited_template) > threshold:
                st.warning(f"Text length: {len(edited_template)}")
            edited_templates.append(edited_template)
        edited_templates_dict[headline] = edited_templates
    return edited_templates_dict

def filter_rows(group):
    if len(group) == 1:  # If only one row in the group, keep it
        return group
    else:  # If more than one row in the group
        # 1. Prefer multi-day campaigns over one-day campaigns
        non_one_day_group = group[~group['Labels'].str.contains('one', case=False, na=False)]
        if not non_one_day_group.empty:
            # 3. Prefer specific percentages over "20-50%" within 10-day campaigns
            specific_percentage_group = non_one_day_group[~non_one_day_group['rabat'].str.contains('20-50%', case=False, na=False)]
            if not specific_percentage_group.empty:
                # 4. Prefer the lowest percentage within specific percentage 10-day campaigns
                specific_percentage_group['numeric_percentage'] = specific_percentage_group['rabat'].str.rstrip('%').astype(float)
                return specific_percentage_group.nsmallest(1, 'numeric_percentage')
            else:
                return non_one_day_group
        else:
            # 3. Prefer specific percentages over "20-50%" within one-day campaigns other than 12-day campaigns
            specific_percentage_group = group[~group['rabat'].str.contains('20-50%', case=False, na=False)]
            return specific_percentage_group if not specific_percentage_group.empty else group

def merging(df_new_ads,df_tilbud,df_normal,merge_type):
    df_merged = pd.merge(df_tilbud.assign(temp_key=df_tilbud['Ad Group'].str.lower()), 
                df_new_ads.assign(temp_key=df_new_ads['brand'].str.lower()), 
                how='inner', 
                left_on='temp_key', 
                right_on='temp_key')
    if merge_type == "Advanced":
        df_tilbud_unmatched = df_tilbud[~df_tilbud['Ad Group'].str.lower().isin(df_merged['temp_key'])]
        df_new_ads_unmatched = df_new_ads[~df_new_ads['brand'].str.lower().isin(df_merged['temp_key'])]
        
        # Count Word Occurrences and get unique words
        word_counts = Counter(itertools.chain(*df_new_ads_unmatched['brand'].str.lower().str.split()))
        unique_words = {word for word, count in word_counts.items() if count == 1}
        
        # Create helper columns for unmatched rows using unique words only
        df_tilbud_unmatched['brand_words'] = df_tilbud_unmatched['Ad Group'].apply(lambda x: set(str(x).lower().split()) & unique_words)
        df_new_ads_unmatched['brand_words'] = df_new_ads_unmatched['brand'].apply(lambda x: set(str(x).lower().split()) & unique_words)
        
        # Initialize a list to hold the rows of the merged DataFrame
        merged_rows = []
        for _, row1 in df_tilbud_unmatched.iterrows():
            for _, row2 in df_new_ads_unmatched.iterrows():
                if len(row1['brand_words'].intersection(row2['brand_words'])) > 0:
                    # Merge the Series by creating a new one from the union of both
                    # Use `.drop` to exclude 'brand_words' and then use `pd.concat` to concatenate the remaining parts
                    merged_row = pd.concat([row1.drop('brand_words'), row2.drop('brand_words')])
                    # Append the merged_row Series to your list of merged rows
                    merged_rows.append(merged_row)
        
        # Construct the merged DataFrame from complex match
        df_complex_matched = pd.DataFrame(merged_rows)

        # Concatenate the results of the exact match and the complex match
        df_merged = pd.concat([df_merged, df_complex_matched], ignore_index=True)

    df_merged = df_merged.drop_duplicates(subset=['Ad Group'], keep='first')

    df_normal_merge = pd.merge(df_merged[['Ad Group', 'Labels']],df_normal, on='Ad Group')

    df_normal_merge['Labels'] = df_normal_merge.apply(lambda row: f"{row['Labels#original']};{row['Labels']}" if pd.notnull(row['Labels#original']) else row['Labels'], axis=1)
    
    # Step 3: Combine 'Labels#original' and 'Labels' columns
    df_merged['Labels'] = df_merged.apply(lambda row: f"{row['Labels#original']};{row['Labels']}" if pd.notnull(row['Labels#original']) else row['Labels'], axis=1)
    
    df_merged.drop(columns=['brand', 'SubCategory', 'rabat', 'period','temp_key','type'], inplace=True)

    return df_merged,df_normal_merge

def data_clean(df_new_ads,df_existing_ads,filter_string,normal_filter_string, edited_headlines, edited_descriptions):
        df_tilbud = df_existing_ads[df_existing_ads['Labels'].str.contains(filter_string, case=False, na=False)]
        df_normal = df_existing_ads[df_existing_ads['Labels'].str.contains(normal_filter_string, case=False, na=False)]
        
        # Rename the columns in existing ads DataFrame to add "#original" to the end of column names where applicable
        original_cols_rename = {col: f"{col}#original" for col in df_existing_ads.columns if ("Headline" in col or "Description" in col) and "position" not in col}
        df_tilbud.rename(columns=original_cols_rename, inplace=True)

        # Generate Texts for New Ads
        df_new_ads = generate_texts(df_new_ads, edited_headlines, edited_descriptions)

        df_new_ads.rename(columns={"label": "Labels"}, inplace=True)

        #df_new_ads = df_new_ads.groupby(['brand']).apply(filter_rows).reset_index(drop=True)
        
        # Step 1: Rename the 'label' column in the original ads DataFrame
        df_tilbud.rename(columns={"Labels": "Labels#original"}, inplace=True)

        df_normal.rename(columns={"Labels": "Labels#original"}, inplace=True)
        return df_new_ads,df_tilbud,df_normal

def main():
    st.title("Generate Headlines and Descriptions for Brands")

    option = st.selectbox("Choose a language for templates", ["Danish", "Swedish"])

    if option == "Danish":
        edited_headlines = display_and_edit_templates(HEADLINES_DANISH, 30)
        edited_descriptions = display_and_edit_templates(DESCRIPTIONS_DANISH, 90)
        filter_string = "RSA Variant: 1"  # Use Danish filter string
        normal_filter_string = "Variant: Normal"
    else:
        edited_headlines = display_and_edit_templates(HEADLINES_SWEDISH, 30)
        edited_descriptions = display_and_edit_templates(DESCRIPTIONS_SWEDISH, 90)
        filter_string = "RSA Variant: 1"   # Use Swedish filter string
        normal_filter_string = "AD-NORMAL"

    merge_type = st.selectbox("Choose Merge Type", ["Default", "Advanced"])

    uploaded_file = st.text_input('Spreadsheet ID', help="Enter the ID of the Google Spreadsheet.")

    if uploaded_file:
        spreadsheet = client.open_by_key(uploaded_file)
        new_ads_sheet = spreadsheet.worksheet('new_ads')
        existing_ads_sheet = spreadsheet.worksheet('existing_ads DK') if option == "Danish" else spreadsheet.worksheet('existing_ads SE')

        # Get all records of the data
        data_new = new_ads_sheet.get_all_records()
        data_existing = existing_ads_sheet.get_all_records()

        # Convert to a DataFrame
        df_new_ads = pd.DataFrame(data_new)

        df_existing_ads = pd.DataFrame(data_existing)

        df_new_ads,df_tilbud,df_normal = data_clean(df_new_ads,df_existing_ads,filter_string,normal_filter_string, edited_headlines, edited_descriptions)
        st.write(df_new_ads,df_tilbud,df_normal)
        df_merged,df_normal_merge = merging(df_new_ads,df_tilbud,df_normal,merge_type)

        # Display the merged DataFrame
        st.write(df_merged)

        st.write(df_normal_merge)

        # Adding a button to download the merged dataframe as an Excel file
        # Adding a button to download the merged dataframe as an Excel file
        advance_merge_sheet_name = 'Tilbud Merge DK' if option == 'Danish' else 'Tilbud Merge SE'
        advance_merge_sheet = spreadsheet.worksheet(advance_merge_sheet_name)
        advance_merge_sheet.clear()
        advance_merge_sheet.insert_rows(df_merged.values.tolist(), row=1)
        advance_merge_sheet.insert_row(df_merged.columns.tolist(), 1)

        # Adding a button to download the merged dataframe as an Excel file
        normal_merge_sheet_name = 'Normal Merge DK' if option == 'Danish' else 'Normal Merge SE'
        normal_merge_sheet = spreadsheet.worksheet(normal_merge_sheet_name)
        normal_merge_sheet.clear()
        normal_merge_sheet.insert_rows(df_normal_merge.values.tolist(), row=1)
        normal_merge_sheet.insert_row(df_normal_merge.columns.tolist(), 1)

if __name__ == "__main__":
    main()
