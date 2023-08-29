import os 
import numpy as np 
import matplotlib.pyplot as plt
import modules.reporter as reporter
from scipy.stats import norm
from fpdf import FPDF
from random import randint
from matplotlib.backends.backend_pdf import PdfPages

MAX_OBSERVATION = 2
RESOLUTION = 60

class PDFContext:
    def __init__(self, filepath):
        self.pdf_pages = PdfPages(filepath)
        
    def save_to_pdf(self, figure):
        self.pdf_pages.savefig(figure)
        
    def close(self):
        self.pdf_pages.close()

def generateID(n = 7): 
    range_start = 10**(n - 1)
    range_end = (10**n) - 1
    return str(randint(range_start, range_end))
    
def printOutputs(curr_params, curr_names, type, curr_period): 
    x = np.linspace(0, MAX_OBSERVATION, RESOLUTION)
    num_plots = len(curr_params.keys())
    num_rows = -(-num_plots // 5)
    fig, axes = plt.subplots(nrows=num_rows, ncols=5, figsize=(10, 2 * num_rows))
    
    for i, name in enumerate(curr_names): 
        row = i // 5
        col = i % 5
        mu, sigma = curr_params[name]
        y = norm.pdf(x, mu, sigma)
        axes[row, col].plot(x, y)
        axes[row, col].set_title(name)
        
    for i in range(num_plots, num_rows * 5):
        row = i // 5
        col = i % 5
        axes[row, col].axis('off')
    
    if type == 'OP': 
        fig.suptitle(f'Observation, Year {curr_period}', fontsize=16)
    if type == 'NOP': 
        fig.suptitle(f'Non-observation, Year {curr_period}', fontsize=16)
    
    plt.tight_layout(rect = [0, 0.02, 1, 0.95])
    return fig, axes

def printOutputsLimit(curr_params, curr_names, curr_period, subplot_layout=(5, 5), save_func=None, type='OP'):
    x = np.linspace(0, MAX_OBSERVATION, RESOLUTION)
    curr_names = list(curr_params.keys())
    num_plots = len(curr_names)
    subplots_per_figure = subplot_layout[0] * subplot_layout[1]
    subplots_counter = 0
    fig = None

    for _, name in enumerate(curr_names):
        if subplots_counter % subplots_per_figure == 0:
            if fig:
                plt.tight_layout(rect=[0, 0.02, 1, 0.95])
                if save_func:
                    save_func(fig)
                plt.close(fig)
            fig, axes = plt.subplots(*subplot_layout, figsize=(10, 2 * subplot_layout[0]))
            fig.suptitle(f'Observation, Year {curr_period}', fontsize=16)  # Moved inside the loop

        row, col = divmod(subplots_counter, subplot_layout[1])
        ax = axes[row][col]

        mu, sigma = curr_params[name]
        y = norm.pdf(x, mu, sigma)
        ax.plot(x, y)
        ax.set_title(name)

        subplots_counter += 1

    # Turn off unused subplots only for the last figure
    for i in range(subplots_counter, subplot_layout[0] * subplot_layout[1]):
        row = i // subplot_layout[1]
        col = i % subplot_layout[1]
        axes[row, col].axis('off')

    if fig:
        plt.tight_layout(rect=[0, 0.02, 1, 0.95])
        if save_func:
            save_func(fig)
        plt.close(fig)

def generateFilepaths(dir_name, id): 
    ranking_output = os.path.join(dir_name, 'rankings_' + id + '.pdf')
    pdf_output = os.path.join(dir_name, 'performance_graphs_' + id + '.pdf')
    dict_output = os.path.join(dir_name, 'performance_values_' + id + '.pdf')
    default_files = (ranking_output, pdf_output, dict_output)
    return default_files

def generateNameFilepaths(dir_name, id, names): 
    namefiles = []
    for name in names: 
        file = os.path.join(dir_name, 'performance_' + name + '_' + id + '.pdf')
        namefiles.append(file)
    return namefiles
    
def generatePerformanceText(name, country, periods, averages_list): 
    text = name + " (" + country + ") " + "\n"
    for period, average in zip(periods, averages_list): 
        text += (str(int(period)) + ": " + str(average) + "\n")
    text + "\n\n"
    return text

def savePDFOutputsToPDF(params, filepath):
    pdf_context = PDFContext(filepath)
    for curr_period in params.keys():
        curr_params = params[curr_period]
        curr_names = params[curr_period].keys()
        printOutputsLimit(curr_params, curr_names, curr_period, save_func = pdf_context.save_to_pdf, type='OP')
    pdf_context.close()
    
# def savePDFOutputsToPDF(params, filepath): 
#     with PdfPages(filepath) as pdf:
#         for curr_period in params.keys(): 
#             curr_names = params[curr_period].keys()
#             fig, axes = printOutputsLimit(params[curr_period], curr_names, curr_period, pdf_context.save_to_pdf)
#             pdf.savefig(fig)
#             plt.close(fig)

def saveDictOutputsToPDF(averages_dict, athlete_data, country_data, filepath):       
    pdf = FPDF()
    pdf.set_font("Arial", size = 10)
    for name in averages_dict: 
        pdf.add_page()
        periods = athlete_data[name].keys()
        averages_list = averages_dict[name]
        text = generatePerformanceText(name, country_data[name], periods, averages_list)
        pdf.multi_cell(0, 8, txt = text)
    pdf.output(filepath, "F")

def saveRankingsToPDF(total_averages_dict, filepath): 
    text = ""
    for i, name in enumerate(total_averages_dict.keys()): 
        text += str(i) + " " + name + ": " + str(total_averages_dict[name]) + "\n"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 10)
    pdf.multi_cell(0, 8, txt = text)
    pdf.output(filepath, "F")
    
def saveOutputs(params, total_averages_dict, averages_dict, athlete_data, country_data, dir_name): 
    id = generateID()
    ranking_filepath, pdf_filepath, dict_filepath = generateFilepaths(dir_name, id)
    print(f'Task {id}')
    print('Saving rankings...')
    saveRankingsToPDF(total_averages_dict, ranking_filepath)
    print('Saved rankings!')
    print('Saving performance values...')
    saveDictOutputsToPDF(averages_dict, athlete_data, country_data, dict_filepath)
    print('Saved performance values!')
    print('Saving performance graphs...')
    print('This may take a few minutes depending on your data size.')
    savePDFOutputsToPDF(params, pdf_filepath)
    print('Saved performance graphs!')
    print('Saving complete!')
      