import geopandas as gpd
from geopandas import GeoDataFrame
from shapely.geometry import Point
from geopy.geocoders import Nominatim
import re
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import itertools
from fuzzywuzzy import fuzz
from collections import OrderedDict
import os
from dotenv import load_dotenv
from unidecode import unidecode

load_dotenv()
city_column = os.getenv('city_column')
latitude_column = os.getenv('latitude_column')
longitude_column = os.getenv('longitude_column')



def CompareLocations(location1, location2):
    # Cleans the locations
    location1 = CleanLocation(location1)
    location2 = CleanLocation(location2)
    # If one of the locations is missing, return false
    if (not location1) or (not location2):
        return False
    # Does a string comparison of the two locations to see if the locations match
    locationMatch = CheckLocationHelper(location1, location2)
    # If a simple string comparison failed, check if the locations are close geographically using geopy
    if locationMatch:
        return True
    else:
        #Tries to geolocate the two written locations
        print("geopy API call")
        geolocator = Nominatim(user_agent='johnnyboi')
        try:
            geo1 = geolocator.geocode(location1)
            coords1 = [geo1.latitude, geo1.longitude]
        except:
            print(f"Location not found: {location1}")
            return False
        try:
            geo2 = geolocator.geocode(location2)
            coords2 = [geo2.latitude, geo2.longitude]
        except:
            print(f"Location not found: {location2}")
            return False
        #Finds the distance between the two locations
        distanceBetweenLocations = geodesic(coords1, coords2).km
        # If within 35 kilometers, returns true. Otherwise, return false.
        if distanceBetweenLocations < 35: #kilometers
            return True
        else:
            return False
    







def CleanLocation(location):
    # Formating
    location = unidecode(location)
    location = location.lower()
    location = location.replace("\n", "") #Removes new line
    location = location.replace(", united states", "") #Removes United States
    location = location.replace(" united states"," ") # removes united states
    location = re.sub(' +', ' ', location) #removes more than one space
    location = re.sub(",$","", location) # removes dangling commas

    # Removes non essential and accidentally included info
    location = location.replace("ril 1950", "").replace("1950","") # Removes 1950
    location = location.replace("township", "") # Removes township
    location = location.replace("judicial", "") # Removes judicial
    location = re.sub("\d", "", location) #removes numbers
    location = re.sub("census", "", location) #removes Census
    location = re.sub("election","",location) #removes election
    location = re.sub("precinct","",location) #removes precinct
    location = re.sub("county","",location) #removes county
    location = re.sub(" ap ", "", location.replace(" apartment ", "")) #removes apartment
    location = re.sub(" ap$", "", location.replace(" apartment$", ""))
    location = re.sub("^ap ", "", location.replace("^apartment ", ""))
    location = re.sub(r'^ap\s', '', location)

    
    # FS is bad with Washington DC. If you put in Washington, "District of Columbia", it will think you are talking about Washington state 
    if ("district of columbia" in location) and (("dc" not in location) and ("d c" not in location)):
        location = location.replace("washington","washington dc")

    # More Formatting
    location = re.sub("  ", "", location) #removes double spaces
    location = re.sub(" $", "", location) #removes space at end
    location = re.sub(" ,", ",", location) #removes space before comma
    location = re.sub(' +', ' ', location) #removes more than one space
    location = re.sub("^ | $","", location) #removes space at end or bevinning
    
    #Removes duplicate places in location (eg. san fransisco, san fransisco, california)
    splitLocation = location.split(",") 
    state = splitLocation[-1]
    city_and_county = [word.strip() for word in splitLocation[:-1]]
    unique_words_in_city_and_county = list(OrderedDict.fromkeys(city_and_county))
    if len(unique_words_in_city_and_county) > 0:
        location = ", ".join(unique_words_in_city_and_county) + f",{state}"
    else:
        location = ", ".join(unique_words_in_city_and_county) + f"{state}"

    #Returns
    return location







def CheckLocationHelper(location1, location2):
    # Split strings into lists of words
    words1 = location1.split(",")
    words2 = location2.split(",")

    # Initialize empty list to store scores
    scores = []

    # Loops through each word in words1 and compare to each word in words2
    for i, word1 in enumerate(words1):
        for j, word2 in enumerate(words2):
            # Gets the score for how well the words match by using fuzz.ratio
            score = fuzz.partial_ratio(word1, word2)
                
            # Add the score to scores
            scores.append((f"{i} words1", f"{j} words2", score))

    # Gets the length of the shortest word
    min_length = min(len(words1), len(words2))

    # Generate all combinations of tuples with length equal to the number of words in string2
    combinations = itertools.combinations(scores, min_length)

    # Filter the combinations to include only valid combinations
    valid_combinations = [c for c in combinations if len(set(x[0] for x in c)) == len(c) and len(set(x[1] for x in c)) == len(c)]

    # Find the combination with the maximum sum
    max_combination = max(valid_combinations, key=lambda x: sum(y[2] for y in x))

    # Cleans the max combo
    cleanedMaxCombination = []
    for tup in max_combination:
        cleanedTup = tuple([s.replace(' words1', '').replace(' words2', '') for s in tup[:2]] + [tup[2]])
        cleanedMaxCombination.append(cleanedTup)

    score = sum(1 for x in cleanedMaxCombination if x[2] >= 85)

    # Returns true if the score is at least 2
    if score >= 2:
        return True
    else:
        return False







def LoadCountiesMap() -> GeoDataFrame:
    # reads the GeoJSON file as a geopandas map
    geojson_file = "_usa_counties.geojson"
    map_geopandas:GeoDataFrame = gpd.read_file(geojson_file)
    return map_geopandas







def GetCountyAndState(latitude, longitude, map) -> tuple[str,str]:
    # Creates a point using coords
    point = Point(longitude, latitude)

    # converts the point to a GeoDataFrame
    points = gpd.GeoDataFrame(geometry=[point])
    points.crs = map.crs

    # performs the join
    result = gpd.sjoin(points, map, predicate='within')

    # gets the county and state information
    try:
        code = int(result['STATEFP'].iloc[0])
        state_codes = {1: 'Alabama', 2: 'Alaska', 4: 'Arizona', 5: 'Arkansas', 6:'California', 8:'Colorado', 9:'Connecticut',
            10:'Delaware', 11: "District of Columbia", 12:'Florida', 13:'Georgia', 15:'Hawaii', 16:'Idaho', 17:'Illinois', 
            18:'Indiana', 19:'Iowa', 20:'Kansas',21:'Kentucky', 22:'Louisiana', 23:'Maine', 24:'Maryland', 25:'Massachusetts', 
            26:'Michigan', 27:'Minnesota', 28:'Mississippi', 29:'Missouri', 30:'Montana', 31:'Nebraska', 32:'Nevada', 
            33:'New Hampshire', 34:'New Jersey', 35:'New Mexico', 36:'New York', 37:'North Carolina', 38:'North Dakota', 
            39:'Ohio', 40:'Oklahoma', 41:'Oregon', 42:'Pennsylvania', 44:'Rhode Island', 45:'South Carolina', 46:'South Dakota',
            47:'Tennessee', 48:'Texas', 49:'Utah', 50:'Vermont', 51:'Virginia', 53:'Washington', 54:'West Virginia', 
            55:'Wisconsin', 56:'Wyoming', 72: "Puerto Rico"
        }
        state = state_codes.get(code)
        county = result['NAME'].iloc[0]

        # Returns as County, State
        return county, state
    
    # if the point is outside the bounds of the map, uses geopy to get the address
    except:
        # Initialize the Nominatim geolocator
        print("geopy API call")
        geolocator = Nominatim(user_agent="johnnyboi")

        # Use the geolocator to get the address of the coordinates
        location = geolocator.reverse(f"{latitude}, {longitude}", exactly_one=True)
        if location == None:
            return "",""
        address = location.raw

        # Extract the county and country from the address
        county = address.get('address').get('county','')
        country = address.get('address').get('country','')

        # Returns as County, Country
        return county, country