# main.py
#gcloud beta run services replace service.yaml


from flask import Flask, send_file
from selenium import webdriver
import chromedriver_binary  # Adds chromedriver binary to path
from google.cloud import storage

app = Flask(__name__)

# The following options are required to make headless Chrome
# work in a Docker container
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("window-size=1024,768")
chrome_options.add_argument("--no-sandbox")

# Initialize a new browser
driver = webdriver.Chrome(chrome_options=chrome_options)

MAX_PAGE_NUM = 5
MAX_PAGE_DIG = 3

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )




def make_blob_public(bucket_name, blob_name):
    """Makes a blob publicly accessible."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.make_public()

    print(
        "Blob {} is publicly accessible at {}".format(
            blob.name, blob.public_url
        )
    )
    return (blob.name, blob.public_url)



@app.route("/")
def hello_world():

    with open("/tmp/results.csv", "w") as f:
        f.write("Buyers, Price \n")


    for i in range(1,MAX_PAGE_NUM):
        page_num = (MAX_PAGE_DIG - len(str(i))) * "0" + str(i)
#add this many 0s to the front as many times as needed based on the len of the current num in compared to the max digit number
        url = "http://econpy.pythonanywhere.com/ex/" + page_num + ".html"
        driver.get(url)
        buyers = driver.find_elements_by_xpath('//div[@title="buyer-name"]')
        prices = driver.find_elements_by_xpath('//span[@class="item-price"]')

        num_page_items = len(buyers)
        with open('/tmp/results.csv', 'a') as f:
            for i in range(num_page_items):
                f.write(buyers[i].text + "," + prices[i].text + "\n")
                print("page saved" + str(i))
        #driver.close()
        upload_blob('bucket-scraping', '/tmp/results.csv', 'results.csv')
        print("uploaded results to bucket-scraping")
        blob_name, blob_url = make_blob_public('bucket-scraping', 'results.csv')
        msg = "Blob " + blob_name + "can be accessed at: " + blob_url
    return msg
