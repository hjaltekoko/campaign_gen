import streamlit as st
import pandas as pd
import io

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
    "Headline 7": [
        "Få {rabat} på {brand} i Magasin",
        "{rabat} på {brand} i Magasin",
        "Super Bazaar i Magasin",
    ],
    "Headline 8": lambda row: [
        "Gælder til d. 8./10." if row['period'] in ["12", 12] else
        "Gælder til d. 1./10." if row['period'] in ["5", 5] else
        "Gælder kun d. 27." if row['period'] == "Onsdag" else
        "Gælder kun d. 30." if row['period'] == "Fredag" else
        "Gælder kun d. 1." if row['period'] == "Lørdag" else
        ""
    ]
}
DESCRIPTIONS_DANISH = {
    "Description 1": [
        "Kom til Super Bazaar i Magasin og få {rabat} på {brand}",
    ],
    "Description 2": [
        "Lige nu får du {rabat} på {brand} - {Headline 5}",
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
    "Headline 7": [  # Add more Swedish templates here
        "Mid Season Sale på Magasin.se",
    ],
    "Headline 8": lambda row: [
        "Gäller fram till den 8/10" if row['period'] in ["12", 12] else
        "Gäller fram till den 1/10" if row['period'] in ["5", 5] else
        "Gäller bara idag den 27/9" if row['period'] == "Onsdag" else
        "Gäller bara idag den 30/9" if row['period'] == "Fredag" else
        "Gäller bara idag den 1/10" if row['period'] == "Lørdag" else
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
    12: "sb_12_day",
    5: "sb_5_day",
    "Onsdag": "sb_ons_oneday",
    "Fredag": "sb_fre_oneday",
    "Lørdag": "sb_loer_oneday"
}

def generate_texts(df, headlines, descriptions):
    df.rename(columns={"Rabat%_y": "period"}, inplace=True)
    df.rename(columns={"Ws navn": "brand"}, inplace=True)
    df.rename(columns={"Rabat%_x": "rabat"}, inplace=True)

    # Convert numeric 'rabat' values to percentage strings
    df.loc[df['rabat'].apply(lambda x: isinstance(x, (int, float))), 'rabat'] = (df["rabat"] * 100).astype(str) + "%"
    df["rabat"] = df["rabat"].str.replace(".0%", "%", regex=True)
    
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
            # 2. Prefer 12-day campaigns over 5-day campaigns within multi-day campaigns
            twelve_day_group = non_one_day_group[non_one_day_group['Labels'].str.contains('12', case=False, na=False)]
            if not twelve_day_group.empty:
                # 3. Prefer specific percentages over "20-50%" within 12-day campaigns
                specific_percentage_group = twelve_day_group[~twelve_day_group['rabat'].str.contains('20-50%', case=False, na=False)]
                if not specific_percentage_group.empty:
                    # 4. Prefer the lowest percentage within specific percentage 12-day campaigns
                    specific_percentage_group['numeric_percentage'] = specific_percentage_group['rabat'].str.rstrip('%').astype(float)
                    return specific_percentage_group.nsmallest(1, 'numeric_percentage')
                else:
                    return twelve_day_group
            else:
                # 3. Prefer specific percentages over "20-50%" within multi-day campaigns other than 12-day campaigns
                specific_percentage_group = non_one_day_group[~non_one_day_group['rabat'].str.contains('20-50%', case=False, na=False)]
                return specific_percentage_group if not specific_percentage_group.empty else non_one_day_group
        else:
            # 2. Prefer 12-day campaigns over 5-day campaigns within one-day campaigns
            twelve_day_group = group[group['Labels'].str.contains('12', case=False, na=False)]
            if not twelve_day_group.empty:
                # 3. Prefer specific percentages over "20-50%" within 12-day one-day campaigns
                specific_percentage_group = twelve_day_group[~twelve_day_group['rabat'].str.contains('20-50%', case=False, na=False)]
                if not specific_percentage_group.empty:
                    # 4. Prefer the lowest percentage within specific percentage 12-day one-day campaigns
                    specific_percentage_group['numeric_percentage'] = specific_percentage_group['rabat'].str.rstrip('%').astype(float)
                    return specific_percentage_group.nsmallest(1, 'numeric_percentage')
                else:
                    return twelve_day_group
            else:
                # 3. Prefer specific percentages over "20-50%" within one-day campaigns other than 12-day campaigns
                specific_percentage_group = group[~group['rabat'].str.contains('20-50%', case=False, na=False)]
                return specific_percentage_group if not specific_percentage_group.empty else group



def main():
    st.title("Generate Headlines and Descriptions for Brands")

    option = st.selectbox("Choose a language for templates", ["Danish", "Swedish"])

    if option == "Danish":
        edited_headlines = display_and_edit_templates(HEADLINES_DANISH, 30)
        edited_descriptions = display_and_edit_templates(DESCRIPTIONS_DANISH, 90)
    else:
        edited_headlines = display_and_edit_templates(HEADLINES_SWEDISH, 30)
        edited_descriptions = display_and_edit_templates(DESCRIPTIONS_SWEDISH, 90)

    uploaded_file = st.file_uploader("Choose an Excel file for New Ads", type="xlsx")
    existing_ads_file = st.file_uploader("Choose an Excel file for Existing Ads", type="xlsx")

    if uploaded_file and existing_ads_file:
        df_new_ads = pd.read_excel(uploaded_file)
        df_existing_ads = pd.read_excel(existing_ads_file)

        # Rename the columns in existing ads DataFrame to add "#original" to the end of column names where applicable
        original_cols_rename = {col: f"{col}#original" for col in df_existing_ads.columns if "Headline" in col or "Description" in col}
        df_existing_ads.rename(columns=original_cols_rename, inplace=True)

        # Generate Texts for New Ads
        df_new_ads = generate_texts(df_new_ads, edited_headlines, edited_descriptions)

        df_new_ads.rename(columns={"label": "Labels"}, inplace=True)

        df_new_ads = df_new_ads.groupby(['brand']).apply(filter_rows).reset_index(drop=True)
        
        # Step 1: Rename the 'label' column in the original ads DataFrame
        df_existing_ads.rename(columns={"Labels": "Labels#original"}, inplace=True)

        # Step 2: Perform the merge
        df_merged = pd.merge(df_existing_ads, df_new_ads, how='outer', left_on='Ad Group', right_on='brand')

        # Step 3: Combine 'Labels#original' and 'Labels' columns
        df_merged['Labels'] = df_merged.apply(lambda row: f"{row['Labels#original']};{row['Labels']}" if pd.notnull(row['Labels#original']) else row['Labels'], axis=1)
        
        df_merged.drop(columns=['brand', 'SubCategory', 'rabat', 'period'], inplace=True)

        # Display the merged DataFrame
        st.write(df_merged)

        # Adding a button to download the merged dataframe as an Excel file
        if st.button('Download Merged Data as Excel'):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_merged.to_excel(writer, index=False)
            output.seek(0)
            
            st.download_button(
                label="Download Merged Data as Excel",
                data=output.getvalue(),
                file_name='merged_data.xlsx',
                key='download_excel_merged'
            )

if __name__ == "__main__":
    main()