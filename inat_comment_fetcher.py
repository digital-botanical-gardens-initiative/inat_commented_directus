from pyinaturalist import get_observations
import os
from dotenv import load_dotenv
import requests

load_dotenv()

# import env variable
inat_access_token = os.getenv('INATURALIST_ACCESS_TOKEN')
directus_email = os.getenv('DIRECTUS_EMAIL')
directus_password = os.getenv('DIRECTUS_PASSWORD')

# Define the Directus table url
base_url = 'http://directus.dbgi.org'

# Define the login endpoint URL
login_url = base_url + '/auth/login'

# Create a session object for making requests
session = requests.Session()

# Send a POST request to the login endpoint
response = session.post(login_url, json={'email': directus_email, 'password': directus_password})
data = response.json()['data']
directus_access_token = data['access_token']
collection_url = base_url + '/items/Inaturalist_Commented_Observations/'
session.headers.update({'Authorization': f'Bearer {directus_access_token}'})

#Add headers
headers = {
                'Content-Type': 'application/json'
    }

# We retrieve all observation ids of a project
response = get_observations(
    project_id=130644,
    page='all',
    per_page=200,
    access_token=inat_access_token
)

results = response["results"]
for item in results:

    observation_data = item

    # Filter out observations where comments or identifications are made by a different user
    filtered_comments = [comment for comment in observation_data['comments']]
    filtered_identifications = [identification for identification in observation_data['identifications']]
    id = str(item['id'])

    if len(filtered_identifications)> 1:

        first_identification = filtered_identifications[0]['taxon']['name']
        print("First Identification:", first_identification)

        # Print all other identifications
        other_identifications = ""
        for identification in filtered_identifications[1:]:
            other_identifications += identification['taxon']['name'] + "/"
        
        # Remove the trailing slash and space
        other_identifications = other_identifications.rstrip("/")
        
        # Print the result and count for other identifications
        print("Other Identifications:", other_identifications)

        # Print all comments
        comments_string = ""
        for comment in filtered_comments:
            comments_string += comment['body'] + "/"

        # Remove the trailing slash and space
        comments_string = comments_string.rstrip("/")

        # Print the result and count
        print(comments_string)

        observation_url = "https://www.inaturalist.org/observations/" + id

        data = {'Inat_Id': id,
                'jbuf_taxon': first_identification,
                'proposed_taxons': other_identifications,
                'comments': comments_string,
                'inaturalist_url': observation_url}
        print(data)
        response = session.post(url=collection_url, headers=headers, json=data)
        print(response.status_code)
        if response.status_code != 200:
            collection_url_patch = base_url + '/items/Inaturalist_Commented_Observations/' + id
            response = session.patch(url=collection_url_patch, headers=headers, json=data)
            print(response.status_code)