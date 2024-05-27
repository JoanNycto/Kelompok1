import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text

# Read data from CSV files
data_mvp = pd.read_csv('data_mvp.csv')
data_mvvm = pd.read_csv('data_mvvm.csv')

# Add a column to identify the architecture
data_mvp['Architecture'] = 'MVP'
data_mvvm['Architecture'] = 'MVVM'

# Combine the data
data = pd.concat([data_mvp, data_mvvm])

# Define the categories and values columns
categories_columns = ['view_total', 'spin_total']
values_columns = ['time', 'memory']

# Define colors for each architecture
colors = {'MVP': 'skyblue', 'MVVM': 'lightgreen'}

for category_column in categories_columns:
    for value_column in values_columns:
        plt.figure(figsize=(20, 10))  # Increase figure size
        grouped_data = {}

        # Prepare grouped data for both architectures
        for architecture in ['MVP', 'MVVM']:
            arch_data = data[data['Architecture'] == architecture]
            categories = arch_data[category_column]
            values = arch_data[value_column]
            grouped_data[architecture] = {category: [] for category in sorted(categories.unique())}
            for category, value in zip(categories, values):
                grouped_data[architecture][category].append(value)

        # Create boxplots for each architecture
        all_categories = sorted(set(grouped_data['MVP'].keys()).union(set(grouped_data['MVVM'].keys())))
        positions = np.arange(len(all_categories)) * 2
        width = 0.4

        for i, (architecture, arch_grouped_data) in enumerate(grouped_data.items()):
            pos = positions + (i * width)
            box_data = [arch_grouped_data.get(cat, []) for cat in all_categories]
            bp = plt.boxplot(box_data,
                             positions=pos,
                             widths=width,
                             patch_artist=True,
                             showfliers=False,
                             boxprops=dict(facecolor=colors[architecture], color='black'),
                             medianprops=dict(color='black'))

        # Add labels and title
        plt.xticks(positions + width / 2, [f'{cat}' for cat in all_categories])  # Set x-axis labels only once per category
        plt.xlabel(category_column.replace("_", " ").capitalize())  # Use category column as xlabel
        plt.title(f'Boxplot of {value_column.capitalize()} by {category_column.replace("_", " ").capitalize()}')
        plt.ylabel(value_column.capitalize())

        # Add legend
        handles = [plt.plot([], [], color=colors[architecture], label=architecture)[0] for architecture in colors.keys()]
        plt.legend(handles=handles, loc='upper right')

        # Add median, Q1, Q3 annotations without overlap
        texts = []  # Store texts for later adjustment
        for j, (architecture, arch_grouped_data) in enumerate(grouped_data.items()):
            for k, category in enumerate(all_categories):
                data_values = arch_grouped_data.get(category, [])
                if not data_values:  # Skip if no data for this category
                    continue

                median = np.median(data_values)
                q1 = np.percentile(data_values, 25)
                q3 = np.percentile(data_values, 75)
                avg = np.mean(data_values)

                # Calculate text positions to avoid overlap
                text_y = [q1 - 0.03 * np.ptp(plt.ylim()), median - 0.01 * np.ptp(plt.ylim()), q3 + 0.03 * np.ptp(plt.ylim())]
                offset = -0.20 if architecture == 'MVP' else 0.20  # Offset to left for MVP, right for MVVM
                for l, (text, value) in enumerate(zip(['Q1', 'Med.', 'Q3'], [q1, median, q3])):  # Use abbreviations
                    texts.append(plt.text(positions[k] + (j * width) + offset, text_y[l], f'{text}={int(value)}', ha='center', va='top', fontsize=8))  # Decrease font size

                # Add average annotation with an offset
                plt.scatter(positions[k] + (j * width) + offset, avg, marker='x', color='black', zorder=5)  # Add 'X' symbol for average
                texts.append(plt.text(positions[k] + (j * width) + offset, avg + 0.01 * np.ptp(plt.ylim()), f'Avg={int(avg)}', ha='center', va='bottom', fontsize=8))  # Decrease font size

        # Adjust text to avoid overlap
        adjust_text(texts, only_move={'points':'y', 'texts':'y'}, arrowprops=dict(arrowstyle="->", color='r', lw=0.5))

        # Save plot to a PDF file
        plt.savefig(f'plot_{category_column}_{value_column}.pdf', bbox_inches='tight', pad_inches=0.2, dpi=300, format='pdf', transparent=True)
        plt.show()  # Show the plot for review

print("Done!")
