
from plotnine import *
from PIL import Image
import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager

def prepare_disease_data(df, disease):
    """
    Prepare disease data for plotting.

    Parameters:
    - df: A pandas DataFrame with 'Diseases', 'Date', 'Cases', and 'Deaths' columns.
    - disease: The name of the disease to filter the DataFrame on.

    Returns:
    - A pandas DataFrame processed to include only the relevant disease data, with missing dates filled in.
    """
    # Filter data for the specified disease
    disease_data = df[df['Diseases'] == disease].copy()
    # formate date
    disease_data['Date'] = pd.to_datetime(disease_data['Date']).dt.date
    disease_data = disease_data.sort_values(by='Date', ascending=True)
    # drop unnecessary columns
    disease_data = disease_data[['YearMonthDay', 'Cases', 'Deaths']]
    # complete missing dates
    dates_unrecognized = pd.date_range(disease_data['YearMonthDay'].min(), disease_data['YearMonthDay'].max(), freq='MS').strftime('%Y/%m/%d')
    dates_unrecognized = list(set(dates_unrecognized) - set(disease_data['YearMonthDay']))
    missing_data = pd.DataFrame({'YearMonthDay': dates_unrecognized, 'Cases': None, 'Deaths': None})
    disease_data = pd.concat([disease_data, missing_data])
    # sort by date
    disease_data = disease_data.sort_values(by='YearMonthDay', ascending=True)
    disease_data = disease_data.reset_index()
    disease_data = disease_data.drop(['index'], axis=1)
    # formate date
    disease_data['Date'] = pd.to_datetime(disease_data['YearMonthDay'])
    disease_data['YearMonth'] = disease_data['Date'].dt.strftime('%Y %B')

    # table
    disease_data['Year'] = disease_data['Date'].dt.year
    disease_data['Month'] = disease_data['Date'].dt.month
    disease_data = disease_data.drop_duplicates(subset=['Year', 'Month'])
    
    return disease_data

def plot_disease_data(disease_data, disease, output_folder="temp"):
    """
    Plot disease cases and deaths over time and save the figure as a PNG file.

    Parameters:
    - disease_data: A pandas DataFrame with 'Date', 'Cases', and 'Deaths' columns.
    - output_folder: The output directory to save the figure.
    """
    # set font
    font_manager.fontManager.addfont('./WeeklyReport/font/Helvetica.ttf')
    matplotlib.rcParams['font.family'] = 'Helvetica'

    # Create a figure with a single subplot
    fig, ax1 = plt.subplots(figsize=(343.5/40, 165/40))

    # Plot cases on the primary y-axis
    ax1.plot(disease_data['Date'], disease_data['Cases'], color="#0072B5FF")
    ax1.tick_params(axis='y', colors='#0072B5FF')
    ax1.spines['left'].set_color('#0072B5FF')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.set_ylim(bottom=0)
    ax1.set_ylabel("Cases", color="#0072B5FF", rotation=0, va='bottom', ha='left', y=1, labelpad=0, fontweight='bold', fontsize=14)

    # Plot deaths on the secondary y-axis
    ax2 = ax1.twinx()
    ax2.plot(disease_data['Date'], disease_data['Deaths'], color="#BC3C29FF")
    ax2.tick_params(axis='y', colors='#BC3C29FF')
    ax2.spines['right'].set_color('#BC3C29FF')
    ax2.spines['top'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.set_ylim(bottom=0)
    ax2.set_ylabel("Deaths", color="#BC3C29FF", rotation=0, va='bottom', ha='left', y=1, labelpad=-25, fontweight='bold', fontsize=14)

    # Set the x-axis with date formatting
    years = matplotlib.dates.YearLocator()
    years_fmt = matplotlib.dates.DateFormatter('%Y')
    ax1.set_xlim([max(disease_data['Date']) - pd.DateOffset(years=10), max(disease_data['Date']) + pd.DateOffset(months=3)])
    ax1.xaxis.set_major_locator(years)
    ax1.xaxis.set_major_formatter(years_fmt)

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Save the figure
    disease_chart_path = os.path.join(output_folder, f"{disease} figure1.png")
    plt.subplots_adjust(left=0.1, right=0.9, top=0.95, bottom=0.05)
    plt.savefig(disease_chart_path, transparent=True, dpi=300)
    plt.close()

    return disease_chart_path

def plot_disease_heatmap(disease_data, disease, output_folder="temp"):
    """
    Plot disease cases and deaths over time and save the figure as a PNG file.

    Parameters:
    - disease_data: A pandas DataFrame with 'Date', 'Cases', and 'Deaths' columns.
    - output_folder: The output directory to save the figure.
    """
    
    data = disease_data.copy()
    data = data.melt(id_vars=['Year', 'Month', 'YearMonth'],
                      value_vars=['Cases', 'Deaths'],
                      var_name='Type',
                      value_name='Value')
    data['Value'] = pd.to_numeric(data['Value'], errors='coerce')

    # plot heatmap for cases
    plot_case = (
            ggplot(data[(data['Value'] != -10) & (data['Type'] == 'Cases')],
                    aes(y='factor(Year)', x='factor(Month)', fill='Value')) +
            geom_tile(aes(width=.95, height=.95)) +
            scale_fill_gradient2(limits=[0, None],
                                 low="#AFDFEFFF",
                                 high="#172869FF") +
            coord_equal() +
            theme_bw() +
            theme(panel_grid=element_blank(),
                  plot_background=element_rect(fill="#E6E6E6"),
                  panel_background=element_rect(fill="#E6E6E6"),
                  legend_background=element_rect(fill="#E6E6E6"),
                  legend_position='right') +
            labs(x='', y='', fill='Cases') +
            guides(fill = guide_colorbar(title = "Cases", barwidth = 5, barheight = 22))
    )
    plot_case.save(os.path.join(output_folder, f"{disease} figure2_1.png"), dpi=300, width = 4.85, height = 3)

    # plot heatmap for deaths
    plot_death = (
            ggplot(data[(data['Value'] != -10) & (data['Type'] == 'Deaths')],
                    aes(y='factor(Year)', x='factor(Month)', fill='Value')) +
            geom_tile(aes(width=.95, height=.95)) +
            scale_fill_gradient2(limits=[0, None],
                                 low="#FECEA8FF",
                                 high="#96281BFF") +
            coord_equal() +
            theme_bw() +
            theme(panel_grid=element_blank(),
                  plot_background=element_rect(fill="#E6E6E6"),
                  panel_background=element_rect(fill="#E6E6E6"),
                  legend_background=element_rect(fill="#E6E6E6"),
                  legend_position='right') +
            labs(x='', y='', fill='Deaths') +
            guides(fill = guide_colorbar(title = "Deaths", barwidth = 5, barheight = 22))
    )
    plot_death.save(os.path.join(output_folder, f"{disease} figure2_2.png"), dpi=300, width = 4.85, height = 3)

    # combine two heatmap
    img1 = Image.open(os.path.join(output_folder, f"{disease} figure2_1.png"))
    img1 = img1.crop((10, 10, img1.width-10, img1.height-10))
    img2 = Image.open(os.path.join(output_folder, f"{disease} figure2_2.png"))
    img2 = img2.crop((10, 10, img2.width-10, img2.height-10))

    total_width = img1.width + img2.width
    max_height = max(img1.height, img2.height)
    # print(total_width, max_height)

    new_im = Image.new('RGB', (total_width, max_height))
    new_im.paste(img1, (0,0))
    new_im.paste(img2, (img1.width,0))

    new_im.save(os.path.join(output_folder, f"{disease} figure2.png"), dpi=(300, 300))

    return output_folder

# Example usage:
# df = pd.read_csv('../../Data/AllData/WeeklyReport/latest.csv', encoding='utf-8')
# df['Date'] = pd.to_datetime(df['Date'])
# disease = 'Hand foot and mouth disease'

# disease_data = prepare_disease_data(df, disease)
# plot_disease_data(disease_data)
# plot_disease_heatmap(disease_data)