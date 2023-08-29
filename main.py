import argparse
import modules.dataProcessor as dp
import modules.iterativeUpdater as iu 
import modules.reporter as rp

def main():
    parser = argparse.ArgumentParser(description='Process PAPERS data and generate reports.')

    parser.add_argument('-f', '--file', required = True, help = 'Path to data file.')
    parser.add_argument('-d', '--destination', required=True, help = 'Destination path for generated reports.')

    args = parser.parse_args()

    period_data, country_data, athlete_data, match_data = dp.processData(args.file, True)
    total_averages_dict, averages_dict, params = iu.PAPERS(period_data, match_data, athlete_data, None, False)
    rp.saveOutputs(params, total_averages_dict, averages_dict, athlete_data, country_data, args.destination)

if __name__ == '__main__':
    main()
