#-------------------------------------------------------------------------
# AUTHOR: Roberto Reyes
# FILENAME: parser.py
# SPECIFICATION: This program extracts faculty information from a webpage and stores it in a MongoDB database.
# TIME SPENT: 3 hours
#-----------------------------------------------------------*/
import pymongo
from bs4 import BeautifulSoup
import re


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["crawler_db"]
pages_collection = db["pages"]
professors_collection = db["professors"]

def extract_faculty_info(html):
    soup = BeautifulSoup(html, "html.parser")
    professors = []

    faculty_section = soup.find('section', class_='text-images')
    if not faculty_section:
        print("Faculty section not found.")
        return []

    for member_block in faculty_section.find_all('div', class_='clearfix'):

        name_tags = member_block.find_all('h2')

      
        for name_tag in name_tags:
            name = name_tag.get_text(strip=True) if name_tag else None
            
     
            if not name:
                print("Skipping entry with missing name.")
                continue

            email_tag = name_tag.find_next('a', href=re.compile(r"mailto:"))
            email = email_tag.get('href').replace("mailto:", "") if email_tag else None

            img_tag = name_tag.find_previous('img')
            image_url = img_tag['src'] if img_tag else None

       
            professor = {
                "name": name,
                "email": email,
                "image_url": image_url
            }

            
            professors.append(professor)

    return professors


def store_professors_data(professors):
    if professors:
        professors_collection.insert_many(professors)
        print(f"Inserted {len(professors)} professor records into MongoDB.")

def main():
    
    target_page = pages_collection.find_one({"url": "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"})
    if not target_page:
        print("Faculty page not found in the database.")
        return

    html_content = target_page['html']
    professors = extract_faculty_info(html_content)
    store_professors_data(professors)
   

if __name__ == "__main__":
    main()

