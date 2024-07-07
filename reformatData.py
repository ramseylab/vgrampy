import pandas as pd

# Load the Excel file
file_path = ('txt/2024_06_26_S1/dataframe_log_area_0.006_0_0.15.xlsx', 'txt/2024_06_26_S2/dataframe_log_area_0.006_0_0.15.xlsx', 'txt/2024_06_26_S3/dataframe_log_area_0.006_0_0.15.xlsx')
sheet_number = 1
for i in file_path:
    df = pd.read_excel(i)

    # Pivot the dataframe to achieve the desired structure
    df_pivot = df.pivot_table(index='V', columns=['conc', 'replicate'], values='I')

    # Flatten the MultiIndex columns
    df_pivot.columns = ['_'.join(map(str, col)) for col in df_pivot.columns]

    # Reset the index to make 'V' a column again
    df_pivot.reset_index(inplace=True)

    # Save the transformed dataframe to a new Excel file
    output_file_path = f'transformed_data_S{sheet_number}'
    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        df_pivot.to_excel(writer, index=False)
    sheet_number += 1
 