"""This was only meant for the US, so one of the main purposes of cleanLocation was
to get rid of 'united states' from the location. If you choose to include country,
you will need to modify the helper function in compare_locations.py so that there is 
a higher number of token matches. Ask me about this if that doesn't really make sense."""
from compare_locations import LoadCountiesMap, CleanLocation, CompareLocations
map = LoadCountiesMap() # This map takes awhile to load, so I would make it a global,
                        # so you only have to load it once.
                        # It only works for US counties, but you download another geojson
                        # one off the web to get it to work for Europe or Africa, etc.
location1 = "moorpark, ventura, california" 
location2 = "thousand oaks, california"
location1 = CleanLocation(location1)
location2 = CleanLocation(location2)
results = CompareLocations(location1, location2)
print(results)
print("This comparison required a geopy api call")
print("-------------")

location1 = "moorpark, ventura, california" 
location2 = "moorpark, california"
location1 = CleanLocation(location1)
location2 = CleanLocation(location2)
results = CompareLocations(location1, location2)
print(results)
print("This comparison did not, as there were enough token word matches")
print("", end="\n\n\n")





"""Here is an example of a data object. It is Extremely flexible, even managing to take
trash data. For example:"""
from date_class import Date_Class
trash_date_string = "Do you remember... the 21st night of September?"
my_new_date_object = Date_Class(trash_date_string)
print(my_new_date_object.likely_day)
print(my_new_date_object.likely_month)
print(my_new_date_object.likely_year)
print("----------------------------")
"""This is probably the most ideal format for date, because if a certain field is not set,
it will just be none, and you can make tests for comparing dates when two date objects might
have limited data.
More examples:"""
better_date_string = "11/9/1999"
another_date_object = Date_Class(better_date_string) # Note that it will parse this like a European
print(another_date_object.likely_day)
print(another_date_object.likely_month)
print(another_date_object.likely_year)
print("----------------------------")

better_date_string = "11/23/1999" # unless it's not possible
another_date_object = Date_Class(better_date_string)
print(another_date_object.likely_day)
print(another_date_object.likely_month)
print(another_date_object.likely_year)
print("----------------------------")

better_date_string = "Sep 23 1999" # this works
another_date_object = Date_Class(better_date_string)
print(another_date_object.likely_day)
print(another_date_object.likely_month)
print(another_date_object.likely_year)
print("----------------------------")

better_date_string = "23 Sep 1999" # and so does this
another_date_object = Date_Class(better_date_string)
print(another_date_object.likely_day)
print(another_date_object.likely_month)
print(another_date_object.likely_year)
print("----------------------------")


