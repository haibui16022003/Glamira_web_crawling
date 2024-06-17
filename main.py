from scraper import scrape_site


def main(start_url):
    save_dir = 'images'
    csv_file = 'image_data.csv'
    scrape_site(start_url, save_dir, csv_file)


if __name__ == '__main__':
    main('https://www.glamira.com')
