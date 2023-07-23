import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Function to check if a link works
def is_valid_link(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Extracting the product names from links
def get_product_names_from_url(url):
    try:
        response = requests.get(url)
        # check if the response status is 200 - the site can be accessed
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            # Extract product names
            product_names = soup.select(".product-title")  
            return [product_name.get_text().strip() for product_name in product_names]
        else:
            # If the program fails to retrieve the names from the url, log the error to log.txt
            with open("logs.txt", "a") as log_file:
                log_file.write(f"Failed to retrieve data from: {url}\n")
            return []
    except requests.RequestException as e:
        # If there's an error accessing the url, log the error
        with open("logs.txt", "a") as log_file:
            log_file.write(f"Error while accessing {url}: {e}\n")
        return []

# Reading the csv file line by line
def read_urls_from_file(file_path):
    with open(file_path, "r") as file:
        urls = [line.strip() for line in file]
    return urls

# write the valid links to valid_links.txt, product names to product_names.txt
def write_names_to_files(valid_links_file, product_names_file, product_names_and_links):
    with open(valid_links_file, "w") as valid_file, open(product_names_file, "w") as names_file:
        for product_name, link in product_names_and_links:
            valid_file.write(f"{link}\n")
            names_file.write(f"{product_name}\n")

if __name__ == "__main__":
    # declaring the paths to the input and output files
    input_file_path = "furniture stores pages.csv"  
    valid_links_output_file = "valid_links.txt"
    product_names_output_file = "product_names.txt"

    # Read the urls from the input file
    urls = read_urls_from_file(input_file_path)

    # Making an array for product names and links
    all_product_names_and_links = []
    for url in urls:
        product_names = get_product_names_from_url(url)
        for product_name in product_names:
            # checking if the link works
            if is_valid_link(url):
                all_product_names_and_links.append((product_name, url))

    # Print all the names and links extracted
    print("Extracted Product Names and Links:")
    for product_name, link in all_product_names_and_links:
        print(f"Product Name: {product_name}, Link: {link}")

    # Write all the extracted names and links to separate output files
    write_names_to_files(valid_links_output_file, product_names_output_file, all_product_names_and_links)
    print(f"Valid links have been written to '{valid_links_output_file}'.")
    print(f"Product names have been written to '{product_names_output_file}'.")
